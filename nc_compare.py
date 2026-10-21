"""Cell-by-cell comparison of same-named NetCDF files: results vs reference.

Usage:
    from nc_compare import compare_folders
    report = compare_folders("path/to/results", "path/to/reference")
"""
from pathlib import Path

import h5py                      # NetCDF-4 = HDF5 underneath
import numpy as np


def _compare_arrays(res, ref, tol):
    """Stats of (results - reference) over valid cells."""
    res, ref = res.astype(np.float64), ref.astype(np.float64)
    valid = np.isfinite(res) & np.isfinite(ref)        # ignore NaN/inf
    d = (res - ref)[valid]
    if d.size == 0:
        return {"status": "NO_VALID_CELLS"}
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.abs(d / ref[valid]) * 100              # % relative to reference
    rel = rel[np.isfinite(rel)]
    corr = (np.corrcoef(res[valid], ref[valid])[0, 1]
            if res[valid].std() > 0 and ref[valid].std() > 0 else np.nan)
    if np.array_equal(res, ref, equal_nan=True):
        status = "IDENTICAL"
    elif np.abs(d).max() <= tol:
        status = "WITHIN_TOL"
    else:
        status = "DIFFERENT"
    return {
        "status": status,
        "valid_cells": int(valid.sum()),
        "mean_diff": float(d.mean()),
        "rms_diff": float(np.sqrt((d ** 2).mean())),
        "max_abs_diff": float(np.abs(d).max()),
        "max_rel_diff_pct": float(rel.max()) if rel.size else np.nan,
        "pct_within_tol": float((np.abs(d) <= tol).mean() * 100),
        "correlation": float(corr),
    }


def _sort_values(arr):
    """Flatten, drop NaN/inf, sort lowest -> highest."""
    arr = np.asarray(arr, dtype=np.float64).ravel()
    return np.sort(arr[np.isfinite(arr)])


def compare_folders(results_dir, reference_dir, ordered=False, var="toa", tol=1e-6,
                    pattern="*.nc", verbose=True):
    """Compare files with the same name in results_dir and reference_dir.

    ordered=True: each array is flattened and sorted (lowest -> highest radiance)
    before comparing, i.e. compares value distributions, not pixel positions.

    Returns a dict:
        "files":         {filename: stats dict}
        "only_results":  files missing in reference
        "only_reference": files missing in results
        "all_match":     True if every pair is IDENTICAL/WITHIN_TOL and no files are missing
    """
    results_dir, reference_dir = Path(results_dir), Path(reference_dir)
    for d in (results_dir, reference_dir):
        if not d.is_dir():
            raise NotADirectoryError(d)

    # --- Match by filename ---
    res_files = {f.name for f in results_dir.glob(pattern) if f.is_file()}
    ref_files = {f.name for f in reference_dir.glob(pattern) if f.is_file()}
    common = sorted(res_files & ref_files)

    # --- Compare each pair ---
    files = {}
    for name in common:
        try:
            with h5py.File(results_dir / name) as fr, h5py.File(reference_dir / name) as ff:
                if var not in fr or var not in ff:
                    files[name] = {"status": "VAR_MISSING"}
                    continue
                res, ref = fr[var][()], ff[var][()]
            # --- Optional sorting ---
            if ordered:
                res, ref = _sort_values(res), _sort_values(ref)
            if res.shape != ref.shape:
                files[name] = {"status": f"SHAPE_MISMATCH {res.shape} vs {ref.shape}"}
            else:
                files[name] = _compare_arrays(res, ref, tol)
        except OSError as e:
            files[name] = {"status": f"READ_ERROR: {e}"}

    report = {
        "files": files,
        "only_results": sorted(res_files - ref_files),
        "only_reference": sorted(ref_files - res_files),
    }
    report["all_match"] = (
        all(s["status"] in ("IDENTICAL", "WITHIN_TOL") for s in files.values())
        and not report["only_results"] and not report["only_reference"]
    )

    report["ordered"] = ordered

    if verbose:
        _print_report(report, var, tol)
    return report


def _print_report(report, var, tol):
    """Console summary table."""
    print("\n***** COMPARISON REPORT SUMMARY TABLE *****\n")
    f = report["files"]
    print(f"Variable: {var} | ordered: {report['ordered']} | tol: {tol} | matched: {len(f)} | "
          f"only in results: {len(report['only_results'])} | "
          f"only in reference: {len(report['only_reference'])}")
    print(f"{'file':<40} {'status':<16} {'max|diff|':>11} {'RMS':>11} {'%≤ tol':>8} {'corr':>9}")
    for name, s in f.items():
        if "max_abs_diff" in s:
            print(f"{name:<40} {s['status']:<16} {s['max_abs_diff']:>11.4g} "
                  f"{s['rms_diff']:>11.4g} {s['pct_within_tol']:>8.2f} {s['correlation']:>9.6f}")
        else:
            print(f"{name:<40} {s['status']}")
    for label, key in (("Only in results", "only_results"), ("Only in reference", "only_reference")):
        if report[key]:
            print(f"{label}: {', '.join(report[key])}")
    print("ALL MATCH" if report["all_match"] else "MISMATCHES FOUND")
