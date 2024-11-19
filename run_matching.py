from matching_simulation import MatchingSimulation
from itertools import product
from typing import Dict, List, Tuple

def run_simulation():
    sim = MatchingSimulation()
    all_prefs = sim.generate_all_preferences()
    
    # 存储策略性操作可能带来收益的案例
    beneficial_cases = []
    
    # 遍历所有可能的初始偏好组合
    for s2_pref, s3_pref, c1_pref, c2_pref, c3_pref in product(
        all_prefs['s2'], all_prefs['s3'],
        all_prefs['c1'], all_prefs['c2'], all_prefs['c3']):
        
        # 基准情况：s1诚实申报
        honest_prefs = {
            's1': sim.s1_true_pref,
            's2': s2_pref,
            's3': s3_pref
        }
        school_prefs = {
            'c1': c1_pref,
            'c2': c2_pref,
            'c3': c3_pref
        }
        
        # 运行诚实申报的第一轮
        honest_first_matching = sim.da_algorithm(honest_prefs, school_prefs)
        
        # 生成诚实申报情况下的第二轮偏好更新
        honest_updated_prefs = sim.generate_updated_preferences(
            honest_first_matching, honest_prefs)
        
        # 运行诚实申报的第二轮
        honest_second_matching = sim.da_algorithm({
            's1': sim.s1_true_pref,
            's2': honest_updated_prefs['s2'][0],  # 使用第一个可能的更新
            's3': honest_updated_prefs['s3'][0]
        }, school_prefs)
        
        # 遍历s1的所有可能虚假申报
        for s1_false_pref in all_prefs['s1']:
            if s1_false_pref == sim.s1_true_pref:
                continue
                
            # 运行虚假申报的第一轮
            strategic_first_prefs = {
                's1': s1_false_pref,
                's2': s2_pref,
                's3': s3_pref
            }
            strategic_first_matching = sim.da_algorithm(
                strategic_first_prefs, school_prefs)
            
            # 生成策略性申报情况下的第二轮偏好更新
            strategic_updated_prefs = sim.generate_updated_preferences(
                strategic_first_matching, strategic_first_prefs)
            
            # 运行虚假申报的第二轮（使用真实偏好）
            strategic_second_matching = sim.da_algorithm({
                's1': sim.s1_true_pref,
                's2': strategic_updated_prefs['s2'][0],
                's3': strategic_updated_prefs['s3'][0]
            }, school_prefs)
            
            # 检查是否获得更好的结果
            honest_final_school = honest_second_matching['s1']
            strategic_final_school = strategic_second_matching['s1']
            
            if (sim.s1_true_pref.index(strategic_final_school) < 
                sim.s1_true_pref.index(honest_final_school)):
                beneficial_cases.append({
                    'initial_prefs': honest_prefs,
                    'school_prefs': school_prefs,
                    'strategic_pref': s1_false_pref,
                    'honest_result': honest_final_school,
                    'strategic_result': strategic_final_school
                })
    
    return beneficial_cases

if __name__ == "__main__":
    results = run_simulation()
    print(f"发现 {len(results)} 个有利的策略性操作案例")
    for i, case in enumerate(results, 1):
        print(f"\n案例 {i}:")
        print(f"初始偏好: {case['initial_prefs']}")
        print(f"学校偏好: {case['school_prefs']}")
        print(f"策略性申报: {case['strategic_pref']}")
        print(f"诚实结果: {case['honest_result']}")
        print(f"策略性结果: {case['strategic_result']}") 