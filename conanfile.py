from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    description = "keymap handling library for toolkits and window systems"
    topics = ("conan", "xkbcommon", "keyboard")
    url = "https://github.com/bincrafters/conan-xkbcommon"
    homepage = "https://github.com/xkbcommon/libxkbcommon"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "docs": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": False,
        "docs": False
    }
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is only compatible with Linux")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not tools.which("meson"):
            self.build_requires("meson/0.54.2")
        if not tools.which("bison"):
            self.build_requires("bison/3.5.3")
        if not tools.which("pkg-config"):
            self.build_requires("pkg-config_installer/0.29.2@bincrafters/stable")

    def requirements(self):
        self.requires("xorg/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libxkbcommon-" + self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        defs={
            "enable-wayland": self.options.with_wayland,
            "enable-docs": self.options.docs,
            "enable-x11": self.options.with_x11,
            "libdir": os.path.join(self.package_folder, "lib"),
            "default_library": ("shared" if self.options.shared else "static")}

        meson = Meson(self)
        meson.configure(
            defs=defs,
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder,
            pkg_config_paths=self.build_folder)
        return meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
