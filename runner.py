import os, sys
import argparse
import importlib
from pathlib import Path
from cocotb_tools.runner import get_runner, get_results

# Result conversion
import xml.etree.ElementTree as ET
import json

def add_source_path(dir, pattern, filename):
    for path in Path(dir).rglob('*.py'):
        if path.name.startswith(filename):
            # return path.parent.resolve()
            sys.path.append(str(path.parent.resolve()))

def get_source_paths(dir='.', pattern='*.v', filenames=[]):
    source_paths = []
    for path in Path(dir).rglob(pattern):
        if path.name in filenames:
            source_paths.append(path.resolve())
    return source_paths

def get_points(test_module, test_name):
    module = importlib.import_module(test_module)
    base_test_name = test_name.split('/')[0]
    return getattr(module, base_test_name).points

def test_runner(sources, hdl_toplevel, test_module):
    sim = os.getenv("SIM", "icarus")

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_toplevel,
    )

    res = runner.test(hdl_toplevel=hdl_toplevel, test_module=test_module)
    tree = ET.parse(res)
    root = tree.getroot()
    testcases = root.findall('.//testcase')
    testcases_names = [test.attrib['name'] for test in testcases]
    failures = root.findall('.//testcase/[failure]')
    failure_names = [fail.attrib['name'] for fail in failures]
    return failure_names, testcases_names, get_results(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', default='.')
    parser.add_argument('-t', '--top', required=True)
    parser.add_argument('-s', '--sources', nargs='+', required=True)
    parser.add_argument('-m', '--test-module', required=True)
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('-p', '--points', required=True)

    args = parser.parse_args()

    hdl_toplevel = args.top
    dir = args.dir
    filenames = args.sources
    output_file = args.output
    test_module = args.test_module
    sources = get_source_paths(dir=dir, filenames=filenames)

    add_source_path('.', '*.py', args.test_module)
    test_runner(sources, hdl_toplevel, test_module)
    failed_tests, tests, (n_tests, n_fails) = test_runner(sources, hdl_toplevel, test_module)
    max_points = sum([get_points(test_module, test) for test in tests])
    deductions = 0
    print(f'Max points: {max_points}')
    for fail in failed_tests:
        deductions += get_points(test_module, fail)
    print(f'Incorrect: {len(failed_tests)}')
    print(f'Deductions: {deductions}')
    score = max_points - deductions
    grade = float(args.points) * (float(score) / max_points)
    print(f'Total score: {score}/{max_points} = {grade}')

    output = {
        'score': grade
    }

    with open(output_file, 'w') as f:
        json.dump(output, f)
