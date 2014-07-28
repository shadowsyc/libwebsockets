#!/usr/bin/env python
"""
The script builds OpenCV.framework for iOS.
The built framework is universal, it can be used to build app and run it on either iOS simulator or real device.

Usage:
    ./build_framework.py <outputdir>

By cmake conventions (and especially if you work with OpenCV repository),
the output dir should not be a subdirectory of OpenCV source tree.

Script will create <outputdir>, if it's missing, and a few its subdirectories:

    <outputdir>
        build/
            iPhoneOS-*/
               [cmake-generated build tree for an iOS device target]
            iPhoneSimulator/
               [cmake-generated build tree for iOS simulator]
        opencv2.framework/
            [the framework content]

The script should handle minor OpenCV updates efficiently
- it does not recompile the library from scratch each time.
However, opencv2.framework directory is erased and recreated on each run.
"""

import glob, re, os, os.path, shutil, string, sys

def build_opencv(srcroot, buildroot, target, arch):
    "builds OpenCV for device or simulator"

    builddir = os.path.join(buildroot, target + '-' + arch)
    if not os.path.isdir(builddir):
        os.makedirs(builddir)
    currdir = os.getcwd()
    os.chdir(builddir)
    # for some reason, if you do not specify CMAKE_BUILD_TYPE, it puts libs to "RELEASE" rather than "Release"
    cmakeargs = ("-GXcode " +
                "-DCMAKE_TOOLCHAIN_FILE=%s/ios/cmake/Toolchains/Toolchain-%s_Xcode.cmake " +
                "-DWITH_SSL=1 " +
                "-DWITHOUT_SERVER=1 " +
                "-DWITHOUT_TESTAPPS=1 " +
                "-DCMAKE_INSTALL_PREFIX:PATH=/Users/james/Project/libwebsockets/install") % (srcroot, target)
    # if cmake cache exists, just rerun cmake to update OpenCV.xproj if necessary
    if os.path.isfile(os.path.join(builddir, "CMakeCache.txt")):
        os.system("cmake %s ." % (cmakeargs,))
    else:
        os.system("cmake %s %s" % (cmakeargs, srcroot))

    # for wlib in [builddir + "/modules/world/UninstalledProducts/libopencv_world.a",
    #              builddir + "/lib/Release/libopencv_world.a"]:
    #     if os.path.isfile(wlib):
    #         os.remove(wlib)

    os.system("xcodebuild -parallelizeTargets ARCHS=%s -jobs 8 -sdk %s -configuration Release -target ALL_BUILD" % (arch, target.lower()))
    os.system("xcodebuild ARCHS=%s -sdk %s -configuration Release -target install install" % (arch, target.lower()))
    os.chdir(currdir)

def put_framework_together(srcroot, dstroot):
    "constructs the framework directory after all the targets are built"

    # find the list of targets (basically, ["iPhoneOS", "iPhoneSimulator"])
    targetlist = glob.glob(os.path.join(dstroot, "build", "*"))
    targetlist = [os.path.basename(t) for t in targetlist]

    # set the current dir to the dst root
    currdir = os.getcwd()
    framework_dir = dstroot + "/opencv2.framework"
    if os.path.isdir(framework_dir):
        shutil.rmtree(framework_dir)
    os.makedirs(framework_dir)
    os.chdir(framework_dir)

    # determine OpenCV version (without subminor part)
    tdir0 = "../build/" + targetlist[0]
    cfg = open(tdir0 + "/cvconfig.h", "rt")
    for l in cfg.readlines():
        if l.startswith("#define  VERSION"):
            opencv_version = l[l.find("\"")+1:l.rfind(".")]
            break
    cfg.close()

    # form the directory tree
    dstdir = "Versions/A"
    os.makedirs(dstdir + "/Resources")

    # copy headers
    shutil.copytree(tdir0 + "/install/include/opencv2", dstdir + "/Headers")

    # make universal static lib
    wlist = " ".join(["../build/" + t + "/lib/Release/libopencv_world.a" for t in targetlist])
    os.system("lipo -create " + wlist + " -o " + dstdir + "/opencv2")

    # form Info.plist
    srcfile = open(srcroot + "/ios/Info.plist.in", "rt")
    dstfile = open(dstdir + "/Resources/Info.plist", "wt")
    for l in srcfile.readlines():
        dstfile.write(l.replace("${VERSION}", opencv_version))
    srcfile.close()
    dstfile.close()

    # copy cascades
    # TODO ...

    # make symbolic links
    os.symlink("A", "Versions/Current")
    os.symlink("Versions/Current/Headers", "Headers")
    os.symlink("Versions/Current/Resources", "Resources")
    os.symlink("Versions/Current/opencv2", "opencv2")


def build_framework(srcroot, dstroot):
    "main function to do all the work"

    targets = ["iPhoneOS", "iPhoneOS", "iPhoneSimulator"]
    archs = ["armv7", "armv7s", "i386"]
    for i in range(len(targets)):
        build_opencv(srcroot, os.path.join(dstroot, "build"), targets[i], archs[i])

    # put_framework_together(srcroot, dstroot)
    print("srcroot:"+srcroot+",dstroot:"+dstroot)
    build_root = dstroot+"/build"
    lib_path = "/UninstalledProducts/libwebsockets.a "
    lipo = "xcrun -sdk iphoneos lipo "
    strip = "xcrun -sdk iphoneos strip "
    os.system(lipo + "-create -output " + build_root+"/libwebsockets.a " 
        + build_root+"/iPhoneSimulator-i386"+lib_path
        + build_root+"/iPhoneOS-armv7"+lib_path
        + build_root+"/iPhoneOS-armv7s"+lib_path
        )
    os.system(strip + "-S " + build_root+"/libwebsockets.a")
    os.system(lipo + "-info " + build_root+"/libwebsockets.a")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:\n\t./build_framework.py <outputdir>\n\n"
        sys.exit(0)

    build_framework(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "..")), os.path.abspath(sys.argv[1]))