
# Why 

fmake is based on the idea that project configuration and build logic should remain ordinary Python wherever possible. Rather than introducing a separate language for configuration files, dependency descriptions, and build scripts, fmake makes Python functions discoverable throughout a project.

Functions marked as @fmake.program form the public interface of a project. They can be called from Python, from the fmake command line, or through generated shell bindings. Functions marked as @fmake.target provide reusable internal functionality, such as firmware dependencies.

The FPGA-specific functionality is built on top of this mechanism. pyFirmwareProject represents a Vivado project as a Python object, while targets can add sources, constraints, generated files, simulation infrastructure, or custom Tcl to that project.

The result is that the same language and tooling can be used from high-level project configuration down to the details of generating a Vivado project. There is no separate configuration parser or build-description language, and normal Python features such as type hints, IDE navigation, debugging, environment variables, and reusable libraries remain available throughout the build process.
