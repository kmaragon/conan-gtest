from conans import ConanFile, CMake
import os


channel = os.getenv("CONAN_CHANNEL", "stable")
username = os.getenv("CONAN_USERNAME", "kmaragon")


class GoogletestTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "googlemock/1.8.0@%s/%s" % (username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is in "test_package"
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", "bin", "bin")
        self.copy("*.dylib", "bin", "lib")
        self.copy("*.so", "bin", "lib")

    def test(self):
        os.chdir("bin")
        self.run(".%sexample" % os.sep)
