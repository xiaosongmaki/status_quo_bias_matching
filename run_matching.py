from matching_simulation import MatchingSimulation
from itertools import product
from typing import Dict, List, Tuple
import json
from datetime import datetime

def run_simulation():
    sim = MatchingSimulation()
    all_prefs = sim.generate_all_preferences()
    
    # 存储有利的策略性案例
    beneficial_cases = []
    max_cases = 3  # 进一步限制案例数量
    
    # 大幅减少采样数量
    sample_size = 50  # 减少采样数量
    
    # 准备采样的偏好组合
    preference_combinations = list(product(
        all_prefs['s2'], all_prefs['s3'], all_prefs['s4'],
        all_prefs['c1'], all_prefs['c2'], all_prefs['c3'], all_prefs['c4']
    ))
    
    # 随机采样
    import random
    sampled_combinations = random.sample(preference_combinations, 
                                       min(sample_size, len(preference_combinations)))
    
    simulation_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "sample_size": sample_size,
            "total_combinations": len(preference_combinations)
        },
        "cases": []
    }
    
    # 遍历采样的偏好组合
    for case_index, (s2_pref, s3_pref, s4_pref, c1_pref, c2_pref, c3_pref, c4_pref) in enumerate(sampled_combinations):
        if len(beneficial_cases) >= max_cases:
            break
            
        case_data = {
            "case_id": case_index,
            "initial_setup": {
                "student_preferences": {
                    's1': sim.s1_true_pref,
                    's2': list(s2_pref),
                    's3': list(s3_pref),
                    's4': list(s4_pref)
                },
                "school_preferences": {
                    'c1': list(c1_pref),
                    'c2': list(c2_pref),
                    'c3': list(c3_pref),
                    'c4': list(c4_pref)
                }
            },
            "honest_scenario": {},
            "strategic_scenarios": []
        }
        
        # 基准情况：s1诚实申报
        honest_prefs = {
            's1': sim.s1_true_pref,
            's2': list(s2_pref),
            's3': list(s3_pref),
            's4': list(s4_pref)
        }
        school_prefs = {
            'c1': list(c1_pref),
            'c2': list(c2_pref),
            'c3': list(c3_pref),
            'c4': list(c4_pref)
        }
        
        # 运行诚实申报的第一轮
        honest_first_matching = sim.da_algorithm(honest_prefs, school_prefs)
        
        # 记录诚实情况的数据
        case_data["honest_scenario"] = {
            "first_round": {
                "preferences": honest_prefs,
                "matching": honest_first_matching
            }
        }
        
        # 对s1的虚假申报采样，进一步减少数量
        sampled_s1_prefs = random.sample(list(all_prefs['s1']), 
                                       min(3, len(all_prefs['s1'])))  # 只测试3种虚假申报
        
        for s1_false_pref in sampled_s1_prefs:
            if list(s1_false_pref) == sim.s1_true_pref:
                continue
                
            strategic_scenario = {
                "false_preference": list(s1_false_pref),
                "first_round": {},
                "second_round_scenarios": []
            }
            
            # 运行虚假申报的第一轮
            strategic_first_prefs = {
                's1': list(s1_false_pref),
                's2': list(s2_pref),
                's3': list(s3_pref),
                's4': list(s4_pref)
            }
            strategic_first_matching = sim.da_algorithm(
                strategic_first_prefs, school_prefs)
            
            # 如果第一轮匹配结果与诚实情况相同，跳过这种策略
            if strategic_first_matching == honest_first_matching:
                continue
            
            # 记录第一轮数据
            strategic_scenario["first_round"] = {
                "preferences": strategic_first_prefs,
                "matching": strategic_first_matching
            }
            
            # 生成策略性申报情况下的第二轮偏好更新
            strategic_updated_prefs = sim.generate_updated_preferences(
                strategic_first_matching, strategic_first_prefs)
            
            # 进一步限制每个学生的更新偏好采样数
            max_updates_per_student = 1  # 每个学生只测试1种更新偏好
            sampled_updates = {
                's2': random.sample(strategic_updated_prefs['s2'], 
                                  min(max_updates_per_student, len(strategic_updated_prefs['s2']))),
                's3': random.sample(strategic_updated_prefs['s3'], 
                                  min(max_updates_per_student, len(strategic_updated_prefs['s3']))),
                's4': random.sample(strategic_updated_prefs['s4'], 
                                  min(max_updates_per_student, len(strategic_updated_prefs['s4'])))
            }
            
            # 使用采样后的更新偏好
            for s2_updated_pref in sampled_updates['s2']:
                for s3_updated_pref in sampled_updates['s3']:
                    for s4_updated_pref in sampled_updates['s4']:
                        # 运行虚假申报的第二轮（使用真实偏好）
                        strategic_second_round_prefs = {
                            's1': sim.s1_true_pref,
                            's2': s2_updated_pref,
                            's3': s3_updated_pref,
                            's4': s4_updated_pref
                        }
                        strategic_second_matching = sim.da_algorithm(
                            strategic_second_round_prefs, school_prefs)
                        
                        # 记录每种可能的第二轮情况
                        second_round_scenario = {
                            "updated_preferences": strategic_second_round_prefs,
                            "matching": strategic_second_matching
                        }
                        
                        # 检查是否获得更好的结果（与第一轮诚实结果比较）
                        honest_school = honest_first_matching['s1']
                        strategic_final_school = strategic_second_matching['s1']
                        
                        second_round_scenario["outcome"] = {
                            "honest_result": honest_school,
                            "strategic_result": strategic_final_school,
                            "is_beneficial": (sim.s1_true_pref.index(strategic_final_school) < 
                                            sim.s1_true_pref.index(honest_school))
                        }
                        
                        strategic_scenario["second_round_scenarios"].append(second_round_scenario)
            
            case_data["strategic_scenarios"].append(strategic_scenario)
        
        has_beneficial_strategy = False
        for strategy in case_data["strategic_scenarios"]:
            for second_round in strategy["second_round_scenarios"]:
                if second_round["outcome"]["is_beneficial"]:
                    has_beneficial_strategy = True
                    break
            if has_beneficial_strategy:
                break
        
        if has_beneficial_strategy:
            beneficial_cases.append(case_data)
    
    # 保存数据到JSON文件
    simulation_data["cases"] = beneficial_cases
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"beneficial_simulation_results_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(simulation_data, f, indent=2, ensure_ascii=False)
    
    return simulation_data, filename

def analyze_results(simulation_data, filename: str):
    """分析模拟结果并打印摘要"""
    total_cases = len(simulation_data["cases"])
    beneficial_cases = 0
    total_scenarios = 0
    
    for case in simulation_data["cases"]:
        for strategy in case["strategic_scenarios"]:
            for second_round in strategy["second_round_scenarios"]:
                total_scenarios += 1
                if second_round["outcome"]["is_beneficial"]:
                    beneficial_cases += 1
                
    print(f"\n模拟结果摘要:")
    print(f"总案例数: {total_cases}")
    print(f"总策略组合数: {total_scenarios}")
    print(f"发现的有利策略性操作案例数: {beneficial_cases}")
    print(f"有利策略比例: {beneficial_cases/total_scenarios:.2%}")
    print(f"详细结果已保存到: {filename}")

def save_first_beneficial_case(simulation_data: dict):
    """
    查找并保存第一个包含有利策略的案例
    """
    for case in simulation_data["cases"]:
        for strategy in case["strategic_scenarios"]:
            for second_round in strategy["second_round_scenarios"]:
                if second_round["outcome"]["is_beneficial"]:
                    # 创建一个包含完整上下文的案例数据
                    beneficial_case = {
                        "case_id": case["case_id"],
                        "initial_setup": case["initial_setup"],
                        "honest_scenario": case["honest_scenario"],
                        "beneficial_strategy": {
                            "false_preference": strategy["false_preference"],
                            "first_round": strategy["first_round"],
                            "beneficial_second_round": second_round
                        }
                    }
                    
                    # 保存到新的JSON文件
                    filename = "first_beneficial_case.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(beneficial_case, f, indent=2, ensure_ascii=False)
                    
                    print(f"已找到第一个有利案例并保存到: {filename}")
                    return beneficial_case
    
    print("未找到有利的策略性操作案例")
    return None

def save_all_beneficial_cases(simulation_data: dict):
    """
    查找并保存所有包含有利策略的案例
    """
    beneficial_cases = []
    
    for case in simulation_data["cases"]:
        case_has_beneficial_strategy = False
        beneficial_strategies = []
        
        for strategy in case["strategic_scenarios"]:
            for second_round in strategy["second_round_scenarios"]:
                if second_round["outcome"]["is_beneficial"]:
                    case_has_beneficial_strategy = True
                    beneficial_strategy = {
                        "false_preference": strategy["false_preference"],
                        "first_round": strategy["first_round"],
                        "beneficial_second_round": second_round
                    }
                    beneficial_strategies.append(beneficial_strategy)
        
        if case_has_beneficial_strategy:
            beneficial_case = {
                "case_id": case["case_id"],
                "initial_setup": case["initial_setup"],
                "honest_scenario": case["honest_scenario"],
                "beneficial_strategies": beneficial_strategies
            }
            beneficial_cases.append(beneficial_case)
    
    if beneficial_cases:
        # 保存到新的JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_beneficial_cases_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_beneficial_cases": len(beneficial_cases)
                },
                "cases": beneficial_cases
            }, f, indent=2, ensure_ascii=False)
        
        print(f"已找到 {len(beneficial_cases)} 个有利案例并保存到: {filename}")
        return beneficial_cases
    else:
        print("未找到有利的策略性操作案例")
        return None

if __name__ == "__main__":
    results, filename = run_simulation()
    analyze_results(results, filename)
    save_first_beneficial_case(results)
    save_all_beneficial_cases(results) 