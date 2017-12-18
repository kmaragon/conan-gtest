from conans import ConanFile, CMake, tools
import os

class GooglemockConan(ConanFile):
    name = "googlemock"
    version = "1.8.0"
    license = "BSD 3"
    url = "https://github.com/kmaragon/conan-gtest"
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

        tools.replace_in_file("googlemock/CMakeLists.txt", "project(gmock CXX C)", '''project(gmock CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')


    def build(self):
        cmake = CMake(self)
        
        cmake.configure(source_dir="googlemock")
        cmake.build()  

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.options.main:
            self.cpp_info.libs = ["gmock", "gmock_main"]
        else:
            self.cpp_info.libs = ["gmock"]

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        
        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

