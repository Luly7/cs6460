"""Autograder for the tutorial project.

This autograder runs tests for the tutorial project and formats the output
to match the original autograder format.

Author: George Rudolph, Utah Valley University
Last Modified: 16 Mar 2025

Usage:
    python autograder.py          # Grade all questions
    python autograder.py -q q1    # Grade only question 1
    python autograder.py -q q2    # Grade only question 2
    python autograder.py -q q3    # Grade only question 3

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
and now Utah Valley University.

Attribution Information: The original Pacman AI projects were developed at UC Berkeley.

The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

The autograding code was completely rewritten by George Rudolph, Utah Valley University.
"""

import sys
import time
import subprocess
import re
import contextlib
import argparse
from typing import Dict, List, Any, Optional, Tuple, Union, Set


# Global print muting functionality
_ORIGINAL_STDOUT = None


class WritableNull:
    """File-like object that discards everything written to it."""
    
    def write(self, string: str) -> None:
        """Discard the string."""
        pass
    
    def flush(self) -> None:
        """Do nothing."""
        pass


@contextlib.contextmanager
def muted_print():
    """Context manager that mutes print statements within its scope."""
    global _ORIGINAL_STDOUT
    _ORIGINAL_STDOUT = sys.stdout
    sys.stdout = WritableNull()
    try:
        yield
    finally:
        sys.stdout = _ORIGINAL_STDOUT
        _ORIGINAL_STDOUT = None


def run_tests(questions_to_grade: Optional[Set[str]] = None) -> Dict[str, Any]:
    """Run the tests and return the results.
    
    Args:
        questions_to_grade: Set of question IDs to grade. If None, all questions are graded.
    
    Returns:
        Dictionary containing test results for each question.
    """
    # Import modules to test
    import addition
    import buyLotsOfFruit
    import shop
    import shopSmart
    
    # Initialize results
    results = {}
    all_questions = {"q1", "q2", "q3"}
    
    # If no specific questions are provided, grade all questions
    if questions_to_grade is None:
        questions_to_grade = all_questions
    
    # Test q1: addition
    if "q1" in questions_to_grade:
        results["q1"] = {"tests": [], "passed": True}
        q1_tests = [
            (1, 1, 2),
            (2, 3, 5),
            (10, -2.1, 7.9)
        ]
        
        for i, (a, b, expected) in enumerate(q1_tests):
            with muted_print():
                result = addition.add(a, b)
            
            test_passed = str(result) == str(expected)
            results["q1"]["tests"].append({
                "id": f"test_addition_{i+1}",
                "passed": test_passed,
                "a": a,
                "b": b,
                "expected": expected,
                "result": result
            })
            
            if not test_passed:
                results["q1"]["passed"] = False
    
    # Test q2: buyLotsOfFruit
    if "q2" in questions_to_grade:
        results["q2"] = {"tests": [], "passed": True}
        q2_tests = [
            ([('apples', 2.0), ('pears', 3.0), ('limes', 4.0)], 12.25),
            ([('apples', 4.0), ('pears', 3.0), ('limes', 2.0)], 14.75),
            ([('apples', 2.0), ('strawberries', 2.4375)], 6.4375)
        ]
        
        for i, (order, expected) in enumerate(q2_tests):
            with muted_print():
                result = buyLotsOfFruit.buyLotsOfFruit(order)
            
            test_passed = str(result) == str(expected)
            results["q2"]["tests"].append({
                "id": f"test_buy_lots_of_fruit_{i+1}",
                "passed": test_passed,
                "order": order,
                "expected": expected,
                "result": result
            })
            
            if not test_passed:
                results["q2"]["passed"] = False
    
    # Test q3: shopSmart
    if "q3" in questions_to_grade:
        results["q3"] = {"tests": [], "passed": True}
        
        # Test 1: shop1 is cheaper for apples and oranges
        with muted_print():
            dir1 = {'apples': 2.0, 'oranges': 1.0}
            shop1 = shop.FruitShop('shop1', dir1)
            dir2 = {'apples': 1.0, 'oranges': 5.0}
            shop2 = shop.FruitShop('shop2', dir2)
            shops = [shop1, shop2]
            order = [('apples', 1.0), ('oranges', 3.0)]
            result = shopSmart.shopSmart(order, shops)
            expected = shop1
        
        test_passed = result and result.getName() == expected.getName()
        results["q3"]["tests"].append({
            "id": "test_shop_smart_1",
            "passed": test_passed,
            "expected": expected,
            "result": result
        })
        
        if not test_passed:
            results["q3"]["passed"] = False
        
        # Test 2: shop2 is cheaper for apples only
        with muted_print():
            order = [('apples', 3.0)]
            result = shopSmart.shopSmart(order, shops)
            expected = shop2
        
        test_passed = result and result.getName() == expected.getName()
        results["q3"]["tests"].append({
            "id": "test_shop_smart_2",
            "passed": test_passed,
            "expected": expected,
            "result": result
        })
        
        if not test_passed:
            results["q3"]["passed"] = False
        
        # Test 3: shop3 is cheaper for apples and oranges
        with muted_print():
            dir3 = {'apples': 1.0, 'oranges': 1.0}
            shop3 = shop.FruitShop('shop3', dir3)
            shops = [shop1, shop2, shop3]
            order = [('apples', 1.0), ('oranges', 1.0)]
            result = shopSmart.shopSmart(order, shops)
            expected = shop3
        
        test_passed = result and result.getName() == expected.getName()
        results["q3"]["tests"].append({
            "id": "test_shop_smart_3",
            "passed": test_passed,
            "expected": expected,
            "result": result
        })
        
        if not test_passed:
            results["q3"]["passed"] = False
    
    return results


def format_output(results: Dict[str, Any]) -> None:
    """Format the output to match the original autograder."""
    # Print header
    start_time = time.strftime("%m-%d at %H:%M:%S", time.localtime())
    print(f"Starting on {start_time}")
    print()
    
    # Print results for each question
    for question_id in sorted(results.keys()):
        question = results[question_id]
        
        print(f"Question {question_id}")
        print("===========")
        print()
        
        # Print test results
        if question_id == "q1":
            success_msg = "add(a,b) returns the sum of a and b"
            failure_msg = "add(a,b) must return the sum of a and b"
            
            for test in question["tests"]:
                if test["passed"]:
                    print(f"*** PASS: {success_msg}")
                    print(f"***      correct result: \"{test['expected']}\"")
                else:
                    print(f"*** FAIL: {failure_msg}")
                    print(f"***      student result: \"{test['result']}\"")
                    print(f"***      correct result: \"{test['expected']}\"")
        
        elif question_id == "q2":
            success_msg = "buyLotsOfFruit correctly computes the cost of the order"
            failure_msg = "buyLotsOfFruit must compute the correct cost of the order"
            
            for test in question["tests"]:
                if test["passed"]:
                    print(f"*** PASS: {success_msg}")
                    print(f"***      correct result: \"{test['expected']}\"")
                else:
                    print(f"*** FAIL: {failure_msg}")
                    print(f"***      student result: \"{test['result']}\"")
                    print(f"***      correct result: \"{test['expected']}\"")
        
        elif question_id == "q3":
            success_msg = "shopSmart(order, shops) selects the cheapest shop"
            failure_msg = "shopSmart(order, shops) must select the cheapest shop"
            
            for i, test in enumerate(question["tests"]):
                shop_num = i + 1
                if test["passed"]:
                    print(f"*** PASS: {success_msg}")
                    print(f"***      correct result: \"<FruitShop: shop{shop_num}>\"")
                else:
                    print(f"*** FAIL: {failure_msg}")
                    if test["result"]:
                        print(f"***      student result: \"{test['result']}\"")
                    else:
                        print(f"***      student result: \"None\"")
                    print(f"***      correct result: \"<FruitShop: shop{shop_num}>\"")
        
        # Print score
        score = 1 if question["passed"] else 0
        print()
        print(f"### Question {question_id}: {score}/1 ###")
        print()
        print()
    
    # Print summary
    end_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"Finished at {end_time}")
    print()
    print("Provisional grades")
    print("==================")
    
    total_score = sum(1 if q["passed"] else 0 for q in results.values())
    total_possible = len(results)
    
    for question_id in sorted(results.keys()):
        score = 1 if results[question_id]["passed"] else 0
        print(f"Question {question_id}: {score}/1")
    
    print("------------------")
    print(f"Total: {total_score}/{total_possible}")
    print()
    print("Your grades are NOT yet registered. To register your grades, make sure")
    print("to follow your instructor's guidelines to receive credit on your project.")


def parse_args() -> Optional[Set[str]]:
    """Parse command line arguments.
    
    Returns:
        Set of question IDs to grade, or None to grade all questions.
    """
    parser = argparse.ArgumentParser(description='Grade the tutorial project.')
    parser.add_argument('-q', '--question', dest='question',
                        help='Grade only the specified question (e.g., q1, q2, q3)')
    
    args = parser.parse_args()
    
    if args.question:
        if args.question not in {'q1', 'q2', 'q3'}:
            print(f"Error: Unknown question '{args.question}'")
            print("Valid questions are: q1, q2, q3")
            sys.exit(1)
        return {args.question}
    
    return None


def main() -> None:
    """Run the tests and format the output."""
    questions_to_grade = parse_args()
    results = run_tests(questions_to_grade)
    format_output(results)


if __name__ == "__main__":
    main() 