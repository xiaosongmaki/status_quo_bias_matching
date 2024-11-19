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
        
        # 生成诚实申报情况下的第二轮偏好更新
        honest_updated_prefs = sim.generate_updated_preferences(
            honest_first_matching, honest_prefs)
        
        # 运行诚实申报的第二轮
        honest_second_round_prefs = {
            's1': sim.s1_true_pref,
            's2': honest_updated_prefs['s2'][0],
            's3': honest_updated_prefs['s3'][0]
        }
        honest_second_matching = sim.da_algorithm(honest_second_round_prefs, school_prefs)
        
        # 记录诚实情况的数据
        case_data["honest_scenario"] = {
            "first_round": {
                "preferences": honest_prefs,
                "matching": honest_first_matching
            },
            "second_round": {
                "updated_preferences": honest_second_round_prefs,
                "matching": honest_second_matching
            }
        }
        
        # 遍历s1的所有可能虚假申报
        for s1_false_pref in all_prefs['s1']:
            if list(s1_false_pref) == sim.s1_true_pref:
                continue
                
            strategic_scenario = {
                "false_preference": list(s1_false_pref),
                "first_round": {},
                "second_round": {}
            }
            
            # 运行虚假申报的第一轮
            strategic_first_prefs = {
                's1': list(s1_false_pref),
                's2': list(s2_pref),
                's3': list(s3_pref)
            }
            strategic_first_matching = sim.da_algorithm(
                strategic_first_prefs, school_prefs)
            
            # 记录第一轮数据
            strategic_scenario["first_round"] = {
                "preferences": strategic_first_prefs,
                "matching": strategic_first_matching
            }
            
            # 生成策略性申报情况下的第二轮偏好更新
            strategic_updated_prefs = sim.generate_updated_preferences(
                strategic_first_matching, strategic_first_prefs)
            
            # 运行虚假申报的第二轮（使用真实偏好）
            strategic_second_round_prefs = {
                's1': sim.s1_true_pref,
                's2': strategic_updated_prefs['s2'][0],
                's3': strategic_updated_prefs['s3'][0]
            }
            strategic_second_matching = sim.da_algorithm(
                strategic_second_round_prefs, school_prefs)
            
            # 记录第二轮数据
            strategic_scenario["second_round"] = {
                "updated_preferences": strategic_second_round_prefs,
                "matching": strategic_second_matching
            }
            
            # 检查是否获得更好的结果
            honest_final_school = honest_second_matching['s1']
            strategic_final_school = strategic_second_matching['s1']
            
            strategic_scenario["outcome"] = {
                "honest_result": honest_final_school,
                "strategic_result": strategic_final_school,
                "is_beneficial": (sim.s1_true_pref.index(strategic_final_school) < 
                                sim.s1_true_pref.index(honest_final_school))
            }
            
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
    
    for case in simulation_data["cases"]:
        for scenario in case["strategic_scenarios"]:
            if scenario["outcome"]["is_beneficial"]:
                beneficial_cases += 1
                
    print(f"\n模拟结果摘要:")
    print(f"总案例数: {total_cases}")
    print(f"发现的有利策略性操作案例数: {beneficial_cases}")
    print(f"详细结果已保存到: {filename}")

if __name__ == "__main__":
    results, filename = run_simulation()
    analyze_results(results, filename) 