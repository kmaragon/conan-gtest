from conans import ConanFile, CMake, tools
import os

class GoogletestConan(ConanFile):
    name = "googletest"
    version = "1.8.0"
    license = "BSD 3"
    url = "https://github.com/kmaragon/conan-gtest"
    description = "Conan package for google test framework"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "pthreads": [True, False],
        "hideinternals": [True, False],
        "main": [True, False]
    }
    default_options = "shared=False","pthreads=False","hideinternals=False","main=True"
    generators = "cmake"

    def source(self):
        tools.download("https://github.com/google/googletest/archive/release-%s.zip" % self.version, "googletest.zip")

        tools.unzip("googletest.zip")
        os.unlink("googletest.zip")
        
        self.run("mv googletest*%s/googletest googletest" % self.version)
        tools.replace_in_file("googletest/CMakeLists.txt", "project(gtest CXX C)", '''project(gtest CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.definitions["gtest_disable_pthreads"] = "OFF" if self.options.pthreads else "ON"
        cmake.definitions["gtest_hide_internal_symbols"] = "ON" if self.options.hideinternals else "OFF"
        
        cmake.configure(source_dir="googletest")
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.options.main:
            self.cpp_info.libs = ["gtest_main", "gtest"]
        else:
            self.cpp_info.libs = ["gtest"]

        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        
        if self.settings.os == "Linux" and self.options.pthreads:
            self.cpp_info.libs.append("-pthread")
        
        if self.options.shared:
            self.cpp_info.defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

