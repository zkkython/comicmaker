/**
 * API 测试页面脚本
 */

let testCases = [];
let testResults = {};

document.addEventListener('DOMContentLoaded', () => {
    loadTestCases();
    
    document.getElementById('run-all-btn').addEventListener('click', runAllTests);
    document.getElementById('module-filter').addEventListener('change', filterTestCases);
});

async function loadTestCases() {
    try {
        const response = await fetch('http://localhost:8000/api/test/test-cases');
        const data = await response.json();
        testCases = data.test_cases || [];
        renderTestCases();
    } catch (error) {
        console.error('加载测试用例失败:', error);
        document.getElementById('test-cases-list').innerHTML = 
            '<p class="error">加载测试用例失败: ' + error.message + '</p>';
    }
}

function filterTestCases() {
    const module = document.getElementById('module-filter').value;
    if (module) {
        const filtered = testCases.filter(tc => tc.module === module);
        renderTestCases(filtered);
    } else {
        renderTestCases();
    }
}

function renderTestCases(cases = testCases) {
    const listEl = document.getElementById('test-cases-list');
    
    if (cases.length === 0) {
        listEl.innerHTML = '<p class="loading">暂无测试用例</p>';
        return;
    }
    
    listEl.innerHTML = cases.map(testCase => {
        const status = testResults[testCase.id]?.status || 'pending';
        const statusText = {
            'pending': '未执行',
            'running': '运行中',
            'passed': '通过',
            'failed': '失败'
        }[status] || '未执行';
        
        return `
            <div class="test-case-item" data-test-id="${testCase.id}">
                <div class="test-case-info">
                    <div class="test-case-name">${testCase.name}</div>
                    <div class="test-case-module">${testCase.module}</div>
                </div>
                <div class="test-case-actions">
                    <span class="test-status ${status}">${statusText}</span>
                    <button class="btn btn-primary" onclick="runTestCase('${testCase.id}')" 
                            ${status === 'running' ? 'disabled' : ''}>
                        执行
                    </button>
                    ${testResults[testCase.id] ? `
                        <button class="btn btn-secondary" onclick="showTestDetail('${testCase.id}')">
                            详情
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

async function runTestCase(testCaseId) {
    const testCase = testCases.find(tc => tc.id === testCaseId);
    if (!testCase) return;
    
    // 更新状态为运行中
    testResults[testCaseId] = { status: 'running' };
    renderTestCases();
    
    try {
        const response = await fetch(`http://localhost:8000/api/test/test-cases/${testCaseId}/run`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const result = await response.json();
        
        console.log('Test result:', result); // 调试输出
        
        testResults[testCaseId] = {
            status: result.passed ? 'passed' : 'failed',
            result: result
        };
        
        renderTestCases();
        updateSummary();
        
        // 如果失败，在控制台输出详细信息
        if (!result.passed) {
            console.error('Test failed:', result);
        }
    } catch (error) {
        console.error('执行测试失败:', error);
        testResults[testCaseId] = {
            status: 'failed',
            result: {
                passed: false,
                output: '执行失败: ' + error.message + '\n\n请检查：\n1. 后端服务是否运行在 http://localhost:8000\n2. 后端服务是否已重启加载最新代码\n3. 查看浏览器控制台获取详细错误信息',
                return_code: -1
            }
        };
        renderTestCases();
        updateSummary();
    }
}

async function runAllTests() {
    const module = document.getElementById('module-filter').value;
    const casesToRun = module 
        ? testCases.filter(tc => tc.module === module)
        : testCases;
    
    // 重置所有状态
    casesToRun.forEach(tc => {
        testResults[tc.id] = { status: 'running' };
    });
    renderTestCases();
    
    const btn = document.getElementById('run-all-btn');
    btn.disabled = true;
    btn.textContent = '执行中...';
    
    try {
        const url = module 
            ? `http://localhost:8000/api/test/test-cases/run-all?module=${module}`
            : 'http://localhost:8000/api/test/test-cases/run-all';
        
        const response = await fetch(url, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        const data = await response.json();
        
        // 更新所有结果
        data.results.forEach(result => {
            testResults[result.test_case_id] = {
                status: result.passed ? 'passed' : 'failed',
                result: result
            };
        });
        
        renderTestCases();
        updateSummary(data.summary);
    } catch (error) {
        console.error('批量执行测试失败:', error);
        await showAlertDialog('批量执行测试失败: ' + error.message, '错误');
    } finally {
        btn.disabled = false;
        btn.textContent = '执行所有测试';
    }
}

function updateSummary(summary = null) {
    if (!summary) {
        // 从当前结果计算
        const results = Object.values(testResults);
        summary = {
            total: testCases.length,
            passed: results.filter(r => r.status === 'passed').length,
            failed: results.filter(r => r.status === 'failed').length
        };
    }
    
    document.getElementById('test-summary').style.display = 'flex';
    document.getElementById('total-count').textContent = summary.total;
    document.getElementById('passed-count').textContent = summary.passed;
    document.getElementById('failed-count').textContent = summary.failed;
}

function showTestDetail(testCaseId) {
    const testCase = testCases.find(tc => tc.id === testCaseId);
    const result = testResults[testCaseId];
    
    if (!testCase || !result) return;
    
    document.getElementById('detail-title').textContent = testCase.name;
    
    const detailContent = document.getElementById('test-detail-content');
    const testResult = result.result || {};
    
    detailContent.innerHTML = `
        <div class="test-detail-section">
            <h4>测试信息</h4>
            <div class="test-detail-content">
模块: ${testCase.module}
测试函数: ${testCase.test}
状态: ${result.status === 'passed' ? '通过' : '失败'}
返回码: ${testResult.return_code !== undefined ? testResult.return_code : 'N/A'}
            </div>
        </div>
        ${testResult.output ? `
            <div class="test-detail-section">
                <h4 ${testResult.passed === false ? 'style="color: #e74c3c;"' : ''}>
                    ${testResult.passed === false ? '执行输出（包含错误信息）' : '执行输出'}
                </h4>
                <div class="test-detail-content" ${testResult.passed === false ? 'style="color: #e74c3c;"' : ''}>
                    ${escapeHtml(testResult.output)}
                </div>
            </div>
        ` : testResult.passed === false ? `
            <div class="test-detail-section">
                <h4 style="color: #e74c3c;">错误信息</h4>
                <div class="test-detail-content" style="color: #e74c3c;">
                    测试执行失败，但没有输出详细信息。请检查后端服务是否正常运行。
                </div>
            </div>
        ` : ''}
    `;
    
    const modal = document.getElementById('test-detail-modal');
    modal.showModal();
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function closeTestDetail() {
    const modal = document.getElementById('test-detail-modal');
    modal.close();
}
