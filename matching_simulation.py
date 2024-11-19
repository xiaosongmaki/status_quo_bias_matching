from itertools import permutations
from typing import List, Dict, Tuple, Set

class MatchingSimulation:
    def __init__(self):
        self.students = ['s1', 's2', 's3']
        self.schools = ['c1', 'c2', 'c3']
        self.s1_true_pref = ['c1', 'c2', 'c3']
        
        # 添加调试标志
        self.debug = False
        
    def set_debug(self, debug: bool):
        """设置调试模式"""
        self.debug = debug
        
    def generate_all_preferences(self) -> Dict[str, List[List[str]]]:
        """生成所有可能的偏好排列"""
        all_perms = list(permutations(self.schools))
        result = {
            's1': all_perms,  # s1的所有可能虚假申报
            's2': all_perms,
            's3': all_perms,
            'c1': list(permutations(self.students)),
            'c2': list(permutations(self.students)),
            'c3': list(permutations(self.students))
        }
        
        if self.debug:
            print("生成的所有可能偏好:")
            for agent, prefs in result.items():
                print(f"{agent}的偏好列表: {prefs}")
                print(f"总共{len(prefs)}种可能的排列")
                
        return result
        
    def da_algorithm(self, student_prefs: Dict[str, List[str]], 
                    school_prefs: Dict[str, List[str]]) -> Dict[str, str]:
        """实现DA算法"""
        unmatched_students = self.students.copy()
        school_matches = {school: None for school in self.schools}
        student_proposals = {student: 0 for student in self.students}
        
        if self.debug:
            print("\n开始DA算法匹配过程:")
            print(f"初始学生偏好: {student_prefs}")
            print(f"学校偏好: {school_prefs}")
            
        round_num = 1
        while unmatched_students:
            if self.debug:
                print(f"\n第{round_num}轮匹配:")
                print(f"未匹配学生: {unmatched_students}")
                print(f"当前学校匹配情况: {school_matches}")
            
            # 收集本轮所有未匹配学生的申请
            current_proposals = {}  # school -> [students]
            students_to_remove = []
            
            for student in unmatched_students:
                # 如果学生已申请完所有学校，则加入待移除列表
                if student_proposals[student] >= len(self.schools):
                    if self.debug:
                        print(f"{student}已申请完所有学校")
                    students_to_remove.append(student)
                    continue
                    
                school = student_prefs[student][student_proposals[student]]
                student_proposals[student] += 1
                
                if school not in current_proposals:
                    current_proposals[school] = []
                current_proposals[school].append(student)
                
                if self.debug:
                    print(f"{student}申请{school}")
            
            # 移除已申请完所有学校的学生
            for student in students_to_remove:
                unmatched_students.remove(student)
            
            # 处理每个学校收到的申请
            for school, applicants in current_proposals.items():
                # 将当前匹配的学生也加入考虑
                if school_matches[school] is not None:
                    applicants.append(school_matches[school])
                
                # 按照学校偏好对申请者排序
                applicants.sort(key=lambda x: school_prefs[school].index(x))
                
                # 选择最优的申请者
                best_applicant = applicants[0]
                
                if best_applicant != school_matches[school]:
                    # 如果当前匹配的学生被替换，将其重新加入未匹配列表
                    if school_matches[school] is not None:
                        if self.debug:
                            print(f"{school}接受{best_applicant}, 拒绝{school_matches[school]}")
                        unmatched_students.append(school_matches[school])
                    else:
                        if self.debug:
                            print(f"{school}接受{best_applicant}")
                            
                    school_matches[school] = best_applicant
                    unmatched_students.remove(best_applicant)
                
                # 拒绝其他申请者
                for rejected_student in applicants[1:]:
                    if rejected_student != school_matches[school]:
                        if self.debug:
                            print(f"{school}拒绝{rejected_student}")
                            
            round_num += 1
                    
        final_matching = {student: school for school, student in school_matches.items()}
        if self.debug:
            print("\n最终匹配结果:", final_matching)
        return final_matching
        
    def generate_updated_preferences(self, first_round_matching: Dict[str, str], 
                                   original_prefs: Dict[str, List[str]]) -> Dict[str, List[List[str]]]:
        """生成第二轮可能的偏好更新"""
        updated_prefs = {}
        
        if self.debug:
            print("\n生成更新后的偏好:")
            print(f"第一轮匹配结果: {first_round_matching}")
            print(f"原始偏好: {original_prefs}")
            
        for student in ['s2', 's3']:
            matched_school = first_round_matching[student]
            # 将元组转换为列表
            original_pref = list(original_prefs[student])
            matched_school_index = original_pref.index(matched_school)
            
            if self.debug:
                print(f"\n处理{student}的偏好更新:")
                print(f"匹配到的学校: {matched_school}")
                print(f"原始偏好中的位置: {matched_school_index}")
            
            # 生成所有可能的更新偏好
            possible_prefs = []
            
            # 对于每个可能的新位置（从当前位置到最前面）
            for new_pos in range(matched_school_index + 1):
                # 创建新的偏好列表
                new_pref = original_pref.copy()
                # 将匹配学校移到新位置
                new_pref.remove(matched_school)
                new_pref.insert(new_pos, matched_school)
                possible_prefs.append(new_pref)
                
            updated_prefs[student] = possible_prefs
            
            if self.debug:
                print(f"{student}可能的更新偏好: {updated_prefs[student]}")
                print(f"总共{len(updated_prefs[student])}种可能的更新")
            
        return updated_prefs
    
if __name__ == '__main__':
    # 创建实例并启用调试
    sim = MatchingSimulation()
    sim.set_debug(True)  # 打开调试模式

    # 测试生成偏好
    all_prefs = sim.generate_all_preferences()

    # 测试DA算法
    # 创建一个简单的测试用例
    student_prefs = {
        's1': ['c1', 'c3', 'c2'],
        's2': ['c1', 'c2', 'c3'],
        's3': ['c3', 'c1', 'c2']
    }

    school_prefs = {
        'c1': ['s3', 's2', 's1'],
        'c2': ['s1', 's2', 's3'],
        'c3': ['s1', 's2', 's3']
    }

    # 运行DA算法
    matching_result = sim.da_algorithm(student_prefs, school_prefs)

    # 测试偏好更新
    original_prefs = student_prefs
    updated_prefs = sim.generate_updated_preferences(matching_result, original_prefs)