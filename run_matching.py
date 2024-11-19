from matching_simulation import MatchingSimulation
from itertools import product
from typing import Dict, List, Tuple
import json
from datetime import datetime

def run_simulation():
    sim = MatchingSimulation()
    all_prefs = sim.generate_all_preferences()
    
    # 存储所有运行数据
    simulation_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_combinations": len(list(product(
                all_prefs['s2'], all_prefs['s3'],
                all_prefs['c1'], all_prefs['c2'], all_prefs['c3']
            )))
        },
        "cases": []
    }
    
    # 遍历所有可能的初始偏好组合
    for case_index, (s2_pref, s3_pref, c1_pref, c2_pref, c3_pref) in enumerate(product(
        all_prefs['s2'], all_prefs['s3'],
        all_prefs['c1'], all_prefs['c2'], all_prefs['c3'])):
        
        case_data = {
            "case_id": case_index,
            "initial_setup": {
                "student_preferences": {
                    's1': sim.s1_true_pref,
                    's2': list(s2_pref),
                    's3': list(s3_pref)
                },
                "school_preferences": {
                    'c1': list(c1_pref),
                    'c2': list(c2_pref),
                    'c3': list(c3_pref)
                }
            },
            "honest_scenario": {},
            "strategic_scenarios": []
        }
        
        # 基准情况：s1诚实申报
        honest_prefs = {
            's1': sim.s1_true_pref,
            's2': list(s2_pref),
            's3': list(s3_pref)
        }
        school_prefs = {
            'c1': list(c1_pref),
            'c2': list(c2_pref),
            'c3': list(c3_pref)
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
        
        # 遍历s1的所有可能虚假申报
        for s1_false_pref in all_prefs['s1']:
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
                's3': list(s3_pref)
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
            
            # 考虑所有可能的第二轮偏好更新组合
            for s2_updated_pref in strategic_updated_prefs['s2']:
                for s3_updated_pref in strategic_updated_prefs['s3']:
                    # 运行虚假申报的第二轮（使用真实偏好）
                    strategic_second_round_prefs = {
                        's1': sim.s1_true_pref,
                        's2': s2_updated_pref,
                        's3': s3_updated_pref
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
        
        simulation_data["cases"].append(case_data)
    
    # 保存数据到JSON文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simulation_results_{timestamp}.json"
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

if __name__ == "__main__":
    results, filename = run_simulation()
    analyze_results(results, filename)
    save_first_beneficial_case(results) 