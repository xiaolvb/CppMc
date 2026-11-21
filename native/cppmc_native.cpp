// cppmc_native.cpp — C++17 UI helpers for the CppMc launcher (plain C ABI).
//
// These functions feed the Tkinter window through ctypes: smoothstep easing,
// frame-paced refresh gating and exponential progress catching-up. All of them
// have pure-Python twins in cppmc/native.py, so a missing DLL never breaks the
// launcher; this module only makes the interface glide instead of jump.
//
// Build (MSVC, windows CI):
//   cl /O2 /LD /std:c++17 native\cppmc_native.cpp /Fe:cppmc\native\cppmc_native.dll
//
// Build (MinGW):
//   g++ -O2 -shared -std=c++17 native/cppmc_native.cpp -o cppmc/native/cppmc_native.dll

#include <cmath>
#include <cstdint>

#ifdef _WIN32
#define CPPCMC_EXPORT __declspec(dllexport)
#else
#define CPPCMC_EXPORT
#endif

extern "C" {

// Smoothstep easing: t*t*(3-2t), clamped to [0, 1].
CPPCMC_EXPORT double cppmc_ease(double t) {
    if (t <= 0.0) return 0.0;
    if (t >= 1.0) return 1.0;
    return t * t * (3.0 - 2.0 * t);
}

// Linear interpolation between a and b (t in [0, 1]).
CPPCMC_EXPORT double cppmc_mix(double a, double b, double t) {
    return a + (b - a) * t;
}

// Move shown toward target by factor k each frame (exponential approach).
CPPCMC_EXPORT double cppmc_approach(double shown, double target, double k) {
    return shown + (target - shown) * k;
}

// Frame pace gate: 1 when now - last >= min_interval_ms, else 0.
CPPCMC_EXPORT int cppmc_frame_pace(int64_t now_ms, int64_t last_ms, int min_interval_ms) {
    return (now_ms - last_ms) >= min_interval_ms ? 1 : 0;
}

// Clamp v into [lo, hi].
CPPCMC_EXPORT int cppmc_clip_int(int v, int lo, int hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

}  // extern "C"
