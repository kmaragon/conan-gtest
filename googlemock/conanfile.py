from conans import ConanFile, CMake, tools
import os, re

class GooglemockConan(ConanFile):
    name = "googlemock"
    version = "1.8.0"
    license = "https://raw.githubusercontent.com/google/googletest/master/googletest/LICENSE"
    url = "https://github.com/kmaragon/conan-googletest"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "main": [True, False]
    }
    default_options = "shared=False","main=True"
    generators = "cmake"
    requires = "googletest/%s@kmaragon/stable" % version

    def configure(self):
        self.options["googletest"].shared = self.options.shared
        if self.options.main:
            self.options["googletest"].main = False
        
    def source(self):
        tools.download("https://github.com/google/googletest/archive/release-%s.zip" % self.version, "googletest.zip")

        tools.unzip("googletest.zip")
        os.unlink("googletest.zip")
        
        self.run("mv googletest*%s/googlemock googlemock" % self.version)
        self.run("mv googletest*%s/googletest googlemock/gtest" % self.version)


    def build(self):
        cmake = CMake(self.settings)
        
        tools.replace_in_file("googlemock/CMakeLists.txt", 
                              'if (COMMAND set_up_hermetic_build)',
                              '''include("../conanbuildinfo.cmake")
                              conan_basic_setup()
                              if (COMMAND set_up_hermetic_build)''')
        
        shared = "-DBUILD_SHARED_LIBS=%s" % ("ON" if self.options.shared else "OFF")
        prefix = '-DCMAKE_INSTALL_PREFIX="%s"' % os.path.join(os.getcwd(), "pkg")
        
        self.run('mkdir -p build')
        self.run('mkdir -p pkg')
        self.run('cd build && cmake %s %s -f ../googlemock' % (shared, prefix))
        
        make_options = os.getenv("MAKEOPTS") or ""
        if not re.match("/[^A-z-a-z_-]-j", make_options):
            cpucount = tools.cpu_count()
            make_options += " -j %s" % (cpucount * 2)

        self.run("cd build && make %s %s install" % (cmake.build_config, make_options))

    def package(self):
        self.copy("*gmock*", dst="lib", src="pkg/lib")
        self.copy("*", dst="include/gmock", src="pkg/include/gmock")

    def package_info(self):
        if self.settings.os == "Windows" or self.options.shared:
            if self.options.main:
                self.cpp_info.libs = ["gmock", "gmock_main"]
            else:
                self.cpp_info.libs = ["gmock"]
        else:
            if self.options.main:
                self.cpp_info.libs = [
                    os.path.join(self.package_folder, "lib", "libgmock.a"), 
                    os.path.join(self.package_folder, "lib", "libgmock_main.a")]
            else:
                self.cpp_info.libs = [os.path.join(self.package_folder, "lib", "libgmock.a")]

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        
        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

