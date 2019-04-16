#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
from conans.errors import ConanException
from shutil import copytree
from subprocess import Popen, PIPE, STDOUT
import time


class AndroidSDKConan(ConanFile):
    name = "android-sdk"
    version = "25.2.5"
    description = "Android SDK Tools is a component for the Android SDK. It includes the complete set of development and debugging tools for Android"
    url = "https://github.com/wagcampbell/conan-android-sdk"
    homepage = "https://developer.android.com/studio/releases/sdk-tools"
    license = "Apache 2.0"
    short_paths = True
    no_copy_source = True
    build_requires = "java_installer/8.0.144@bincrafters/stable"
    options = {"buildToolsRevision": "ANY"}
    default_options = "buildToolsRevision=28.0.3"
    settings = {"os_build": ["Windows", "Linux", "Macos"],
                "os": ["Android"]}

    min_api_level = 7
    max_api_level = 28

    def configure(self):
        if int(str(self.settings.os.api_level)) < self.min_api_level or int(str(self.settings.os.api_level)) > self.max_api_level:
            raise ConanException("Unsupported API level: " + str(self.settings.os.api_level) + " (supported [%i ... %i])" % (self.min_api_level, self.max_api_level))

    def source(self):
        if self.settings.os_build == 'Windows':
            source_url = "https://dl.google.com/android/repository/tools_r25.2.5-windows.zip"
            tools.get(source_url, keep_permissions=True)
        elif self.settings.os_build == 'Linux':
            source_url = "https://dl.google.com/android/repository/tools_r25.2.5-linux.zip"
            tools.get(source_url, keep_permissions=True)
        elif self.settings.os_build == 'Macos':
            source_url = "https://dl.google.com/android/repository/tools_r25.2.5-macosx.zip"
            tools.get(source_url, keep_permissions=True)
        else:
            raise ConanException("Unsupported build os: " + self.settings.os_build)

    def build(self):
        if platform.system() == "Windows":
            p1 = Popen(["%s/tools/bin/sdkmanager" % (self.source_folder), ' "platforms;android-%s"' % (str(self.settings.os.api_level))], universal_newlines=True, shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            p1.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
            p2 = Popen(["%s/tools/bin/sdkmanager" % (self.source_folder), ' "build-tools;%s"' % (str(self.options.buildToolsRevision))], universal_newlines=True, shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            p2.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
            p3 = Popen(["%s/tools/bin/sdkmanager" % (self.source_folder), ' "platform-tools"'], universal_newlines=True, shell=True, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            p3.communicate(input='y\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\ny\n')
        else:
            self.run('yes | %s/tools/bin/sdkmanager "platforms;android-%s"' % (self.source_folder, str(self.settings.os.api_level)))
            self.run('yes | %s/tools/bin/sdkmanager "build-tools;%s"' % (self.source_folder, str(self.options.buildToolsRevision)))
            self.run('yes | %s/tools/bin/sdkmanager "platform-tools"' % (self.source_folder))


    sdk_copied = False

    def package(self):
        # Called twice because of 'no_copy_source'. First from source-, then from build-dir
        if not self.sdk_copied:
            copytree("build-tools", self.package_folder + "/build-tools")
            copytree("licenses", self.package_folder + "/licenses")
            copytree("platforms", self.package_folder + "/platforms")
            copytree("tools", self.package_folder + "/tools")
            self.sdk_copied = True

    def package_info(self):
        sdk_root = self.package_folder

        self.output.info('Creating SDK_ROOT, ANDROID_SDK_ROOT, ANDROID_HOME environment variable: %s' % sdk_root)
        self.env_info.SDK_ROOT = sdk_root
        self.env_info.ANDROID_SDK_ROOT = sdk_root
        self.env_info.ANDROID_HOME = sdk_root

        self.output.info('Creating ANDROID_BUILD_TOOLS_REVISION environment variable: %s' % str(self.options.buildToolsRevision))
        self.env_info.ANDROID_BUILD_TOOLS_REVISION = str(self.options.buildToolsRevision)
