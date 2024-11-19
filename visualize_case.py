import json
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List

def load_beneficial_case(filename: str = "first_beneficial_case.json") -> dict:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_preference_str(prefs: List[str]) -> str:
    return " > ".join(prefs)

def create_matching_str(matching: Dict[str, str]) -> str:
    return "\n".join(f"{student}→{school}" for student, school in matching.items())

def visualize_beneficial_case(case_data: dict):
    plt.figure(figsize=(15, 10))
    
    # 创建有向图
    G = nx.DiGraph()
    
    # 添加节点
    nodes = {
        'init': f"初始偏好:\ns1: {create_preference_str(case_data['initial_setup']['student_preferences']['s1'])}\n" +
                f"s2: {create_preference_str(case_data['initial_setup']['student_preferences']['s2'])}\n" +
                f"s3: {create_preference_str(case_data['initial_setup']['student_preferences']['s3'])}",
        
        'honest': f"诚实申报结果:\n{create_matching_str(case_data['honest_scenario']['first_round']['matching'])}",
        
        'strategic_r1': f"策略性申报第一轮:\ns1虚假申报: {create_preference_str(case_data['beneficial_strategy']['false_preference'])}\n" +
                       f"匹配结果:\n{create_matching_str(case_data['beneficial_strategy']['first_round']['matching'])}",
        
        'strategic_r2': f"策略性申报第二轮:\n匹配结果:\n{create_matching_str(case_data['beneficial_strategy']['beneficial_second_round']['matching'])}",
        
        'outcome': f"结果比较:\n诚实结果: s1 → {case_data['beneficial_strategy']['beneficial_second_round']['outcome']['honest_result']}\n" +
                  f"策略结果: s1 → {case_data['beneficial_strategy']['beneficial_second_round']['outcome']['strategic_result']}"
    }
    
    # 添加节点和边
    pos = {
        'init': (0, 0.5),
        'honest': (1, 0.8),
        'strategic_r1': (1, 0.2),
        'strategic_r2': (2, 0.2),
        'outcome': (3, 0.5)
    }
    
    # 添加节点
    for node, label in nodes.items():
        G.add_node(node, label=label)
    
    # 添加边（修改这部分）
    edges = [
        ('init', 'honest'),
        ('init', 'strategic_r1'),
        ('strategic_r1', 'strategic_r2'),
        ('honest', 'outcome'),
        ('strategic_r2', 'outcome')
    ]
    G.add_edges_from(edges)
    
    # 添加边标签
    edge_labels = {
        ('init', 'honest'): '诚实申报',
        ('init', 'strategic_r1'): '策略性申报',
        ('strategic_r1', 'strategic_r2'): '第二轮更新',
        ('honest', 'outcome'): '比较',
        ('strategic_r2', 'outcome'): '比较'
    }
    
    # 绘制图
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=5000, font_size=8, font_weight='bold',
            arrows=True, edge_color='gray',
            labels=nodes)
    
    # 添加边标签
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    plt.title('策略性操作获利流程')
    plt.axis('off')
    
    # 保存图片
    plt.savefig('beneficial_case_visualization.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("可视化图片已保存为: beneficial_case_visualization.png")

if __name__ == "__main__":
    case_data = load_beneficial_case()
    visualize_beneficial_case(case_data) 