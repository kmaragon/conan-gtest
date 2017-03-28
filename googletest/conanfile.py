from conans import ConanFile, CMake, tools
import os, re

class GoogletestConan(ConanFile):
    name = "googletest"
    version = "1.8.0"
    license = "https://raw.githubusercontent.com/google/googletest/master/googletest/LICENSE"
    url = "https://github.com/kmaragon/conan-googletest"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "pthreads": [True, False],
        "hideinternals": [True, False],
        "main": [True, False]
    }
    default_options = "shared=False","pthreads=True","hideinternals=False","main=True"
    generators = "cmake"

    def source(self):
        tools.download("https://github.com/google/googletest/archive/release-%s.zip" % self.version, "googletest.zip")

        tools.unzip("googletest.zip")
        os.unlink("googletest.zip")
        
        self.run("mv googletest*%s/googletest googletest" % self.version)


    def build(self):
        cmake = CMake(self.settings)
        shared = "-DBUILD_SHARED_LIBS=%s" % ("ON" if self.options.shared else "OFF")
        pthreads = "-Dgtest_disable_pthreads=%s" % ("OFF" if self.options.pthreads else "ON")
        hideinternals = "-Dgtest_hide_internal_symbols=%s" % ("ON" if self.options.hideinternals else "OFF")
        prefix = '-DCMAKE_INSTALL_PREFIX="%s"' % self.package_folder
        
        self.run('mkdir -p build')
        self.run('cd build && cmake %s %s %s %s -f ../googletest' % (shared, pthreads, hideinternals, prefix))
        
        make_options = os.getenv("MAKEOPTS") or ""
        if not re.match("/[^A-z-a-z_-]-j", make_options):
            cpucount = tools.cpu_count()
            make_options += " -j %s" % (cpucount * 2)

        self.run("cd build && make %s install" % cmake.build_config)

    def package_info(self):
        if self.settings.os == "Windows" or self.options.shared:
            if self.options.main:
                self.cpp_info.libs = ["gtest", "gtest_main"]
            else:
                self.cpp_info.libs = ["gtest"]
        else:
            if self.options.main:
                self.cpp_info.libs = [
                    os.path.join(self.package_folder, "lib", "libgtest.a"), 
                    os.path.join(self.package_folder, "lib", "libgtest_main.a")]
            else:
                self.cpp_info.libs = [os.path.join(self.package_folder, "lib", "libgtest.a")]

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        
        if self.settings.os == "Linux" and self.options.pthreads:
            self.cpp_info.libs.append("pthread")
        
        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

