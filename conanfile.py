#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os


class XkbcommonConan(ConanFile):
    name = "xkbcommon"
    version = "0.8.2"
    description = "keymap handling library for toolkits and window systems"
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "xkbcommon", "keyboard")
    url = "https://github.com/bincrafters/conan-xkbcommon"
    homepage = "https://xkbcommon.org"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]      # Packages the license for the conanfile.py
    # Remove following lines if the target lib does not use cmake.

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "docs": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": False,
        "docs": False
    }

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("This library is only compatible with Linux")

    def _system_package_architecture(self):
        if tools.os_info.with_apt:
            if self.settings.arch == "x86":
                return ':i386'
            elif self.settings.arch == "x86_64":
                return ':amd64'
            elif self.settings.arch == "armv6" or self.settings.arch == "armv7":
                return ':armel'
            elif self.settings.arch == "armv7hf":
                return ':armhf'
            elif self.settings.arch == "armv8":
                return ':arm64'

        if tools.os_info.with_yum:
            if self.settings.arch == "x86":
                return '.i686'
            elif self.settings.arch == 'x86_64':
                return '.x86_64'
        return ""

    def system_requirements(self):
        pack_names = []
        if tools.os_info.with_apt:
            pack_names.append('xkb-data')
        if self.options.with_x11:
            if tools.os_info.with_apt:
                pack_names += ["libxcb-xkb-dev", "libxcb1-dev"]

        if pack_names:
            installer = tools.SystemPackageTool()
            for item in pack_names:
                installer.install(item + self._system_package_architecture())

    def source(self):
        source_url = "https://github.com/xkbcommon/libxkbcommon"
        tools.get("{0}/archive/xkbcommon-{1}.tar.gz".format(source_url, self.version),
                  sha256="fd19874aefbcbc9da751292ba7abee8952405cd7d9042466e41a9c6ed3046322")
        extracted_dir = "libxkbcommon-" + self.name + "-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        meson = Meson(self)
        meson.configure(defs={
            'enable-wayland': self.options.with_wayland,
            'enable-docs': self.options.docs,
            'enable-x11': self.options.with_x11
        }, source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = Meson(self)
        meson.build_folder = self._build_subfolder
        meson.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs += tools.collect_libs(self)
        if self.options.with_x11:
            self.cpp_info.libs.append('xcb')
            self.cpp_info.libs.append('xcb-xkb')
