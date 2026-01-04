/**
 * 将原始字符串解析为结构化对象数组
 * 支持解析：Thought, Action, Action Input, Final Answer
 */
export function parseReActContent(fullText) {
    // 定义需要匹配的标识符
    const patterns = [
        {label: 'Thought', marker: 'Thought:'},
        {label: 'Action', marker: 'Action:'},
        {label: 'Action Input', marker: 'Action Input:'},
        {label: 'Final Answer', marker: 'Final Answer:'}
    ];

    // 找到所有标识符在字符串中的位置
    let positions = [];
    patterns.forEach(p => {
        let index = fullText.indexOf(p.marker);
        if (index !== -1) {
            positions.push({index, label: p.label, marker: p.marker});
        }
    });

    // 按出现顺序排序
    positions.sort((a, b) => a.index - b.index);

    if (positions.length === 0) {
        // 如果还没匹配到任何标识符，先归类为 Thought (或默认类型)
        return [{type: 'Thought', text: fullText}];
    }

    const result = [];
    for (let i = 0; i < positions.length; i++) {
        const start = positions[i].index + positions[i].marker.length;
        const end = (i + 1 < positions.length) ? positions[i + 1].index : fullText.length;

        // 提取两个标识符之间的文本内容并去除首尾空格
        const content = fullText.substring(start, end).trim();

        result.push({
            type: positions[i].label,
            text: content
        });
    }

    return result;
}


export function createHeaders() {
    const token = localStorage.getItem('token');
    let headers = {
        'Content-Type': 'application/json',
    }
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}