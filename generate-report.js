const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, 
        AlignmentType, WidthType, BorderStyle, ShadingType, LevelFormat, PageBreak,
        Header, Footer, PageNumber } = require('docx');
const fs = require('fs');

// 表格边框样式
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

// 创建文档
const doc = new Document({
    styles: {
        default: {
            document: {
                run: {
                    font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" },
                    size: 24
                }
            }
        },
        paragraphStyles: [
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 36, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" }, color: "667eea" },
                paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 28, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" }, color: "333333" },
                paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 } },
            { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
                run: { size: 24, bold: true, font: { ascii: "Arial", hAnsi: "Arial", eastAsia: "Microsoft YaHei" }, color: "667eea" },
                paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 } },
        ]
    },
    numbering: {
        config: [
            { reference: "bullets",
                levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "numbers",
                levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
        ]
    },
    sections: [{
        properties: {
            page: {
                size: { width: 12240, height: 15840 },
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [new TextRun({ text: "命令注入漏洞报告", size: 20, color: "666666" })]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "第 ", size: 20 }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 20 }),
                        new TextRun({ text: " 页", size: 20 })
                    ]
                })]
            })
        },
        children: [
            // 标题
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 },
                children: [new TextRun({ text: "命令注入漏洞报告", size: 48, bold: true, color: "667eea" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 100 },
                children: [new TextRun({ text: "Ping网络诊断功能安全漏洞分析", size: 28, color: "666666" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 400 },
                children: [new TextRun({ text: "严重程度：高危 (High)", size: 24, bold: true, color: "dc3545" })]
            }),

            // 一、漏洞概述
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("一、漏洞概述")] }),
            
            // 漏洞信息表格
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [2500, 6860],
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 2500, type: WidthType.DXA }, shading: { fill: "f8f9fa", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "漏洞类型", bold: true })] })] }),
                            new TableCell({ borders, width: { size: 6860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("操作系统命令注入 (CWE-78)")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 2500, type: WidthType.DXA }, shading: { fill: "f8f9fa", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "严重程度", bold: true })] })] }),
                            new TableCell({ borders, width: { size: 6860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun({ text: "高危 (High)", bold: true, color: "dc3545" })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 2500, type: WidthType.DXA }, shading: { fill: "f8f9fa", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "CVSS评分", bold: true })] })] }),
                            new TableCell({ borders, width: { size: 6860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("9.8 (Critical)")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 2500, type: WidthType.DXA }, shading: { fill: "f8f9fa", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "影响版本", bold: true })] })] }),
                            new TableCell({ borders, width: { size: 6860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("所有版本")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 2500, type: WidthType.DXA }, shading: { fill: "f8f9fa", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "漏洞位置", bold: true })] })] }),
                            new TableCell({ borders, width: { size: 6860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("/ping 路由")] })] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({ spacing: { before: 200 }, children: [new TextRun("在Ping网络诊断功能中，应用程序使用 subprocess.check_output() 执行系统命令，并且使用 shell=True 参数。由于用户输入的 IP 参数未经任何过滤或验证直接拼接到命令字符串中，攻击者可以通过注入特殊字符执行任意系统命令。")] }),

            // 二、漏洞代码分析
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("二、漏洞代码分析")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 存在漏洞的代码")] }),
            
            new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "关键漏洞代码如下：", italics: true })] }),
            new Paragraph({ spacing: { before: 100, after: 100 }, shading: { fill: "f5f5f5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: "command = f\"ping -n 3 {ip}\"", font: "Courier New", size: 20 })] }),
            new Paragraph({ shading: { fill: "f5f5f5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: "result = subprocess.check_output(command, shell=True, ...)", font: "Courier New", size: 20 })] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 漏洞原因分析")] }),
            
            new Paragraph({ numbering: { reference: "numbers", level: 0 },
                children: [new TextRun({ text: "用户输入未过滤：", bold: true }), new TextRun("IP 参数直接从表单获取，未进行任何格式验证或字符过滤。")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 },
                children: [new TextRun({ text: "字符串直接拼接：", bold: true }), new TextRun("使用 f-string 将用户输入直接拼接到系统命令字符串中。")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 },
                children: [new TextRun({ text: "使用 shell=True：", bold: true }), new TextRun("这个参数允许 shell 解释器解析命令字符串，使得命令分隔符（如 ;、&、|）可以被识别和执行。")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 },
                children: [new TextRun({ text: "缺乏输出过滤：", bold: true }), new TextRun("命令执行结果直接返回给用户，可能泄露敏感系统信息。")] }),

            // 三、攻击演示
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("三、攻击演示")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 攻击Payload示例")] }),
            
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [3500, 2000, 3860],
                rows: [
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, shading: { fill: "667eea", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "Payload", bold: true, color: "FFFFFF" })] })] }),
                            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA }, shading: { fill: "667eea", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "操作系统", bold: true, color: "FFFFFF" })] })] }),
                            new TableCell({ borders, width: { size: 3860, type: WidthType.DXA }, shading: { fill: "667eea", type: ShadingType.CLEAR },
                                children: [new Paragraph({ children: [new TextRun({ text: "执行效果", bold: true, color: "FFFFFF" })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 3500, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun({ text: "127.0.0.1; whoami", font: "Courier New", size: 20 })] })] }),
                            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("Linux/Mac")] })] }),
                            new TableCell({ borders, width: { size: 3860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("执行 ping 后运行 whoami 命令")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 3500, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun({ text: "127.0.0.1 && cat /etc/passwd", font: "Courier New", size: 20 })] })] }),
                            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("Linux/Mac")] })] }),
                            new TableCell({ borders, width: { size: 3860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("显示系统用户列表")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 3500, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun({ text: "127.0.0.1 & whoami", font: "Courier New", size: 20 })] })] }),
                            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("Windows")] })] }),
                            new TableCell({ borders, width: { size: 3860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("执行 whoami 命令")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders, width: { size: 3500, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun({ text: "127.0.0.1 | dir", font: "Courier New", size: 20 })] })] }),
                            new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("Windows")] })] }),
                            new TableCell({ borders, width: { size: 3860, type: WidthType.DXA },
                                children: [new Paragraph({ children: [new TextRun("列出当前目录文件")] })] })
                        ]
                    })
                ]
            }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 攻击流程")] }),
            
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("攻击者登录系统，访问 Ping 测试页面")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("在 IP 输入框中输入恶意 payload，如 127.0.0.1; ls -la")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("点击 Ping 按钮，提交请求")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("服务器执行拼接后的命令：ping -c 3 127.0.0.1; ls -la")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun("攻击者在响应中看到 ls -la 的执行结果")] }),

            // 四、漏洞影响
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("四、漏洞影响")] }),
            
            new Paragraph({ numbering: { reference: "bullets", level: 0 },
                children: [new TextRun({ text: "数据泄露：", bold: true }), new TextRun("攻击者可读取系统任意文件，包括数据库密码、API密钥等敏感信息")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 },
                children: [new TextRun({ text: "系统接管：", bold: true }), new TextRun("攻击者可执行任意命令，完全控制服务器，安装后门或挖矿程序")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 },
                children: [new TextRun({ text: "横向渗透：", bold: true }), new TextRun("以此为跳板攻击内网其他服务器，扩大攻击范围")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 },
                children: [new TextRun({ text: "服务中断：", bold: true }), new TextRun("攻击者可删除关键文件或关闭服务，导致业务中断")] }),

            // 五、修复方案
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("五、修复方案")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 使用参数化命令")] }),
            new Paragraph({ spacing: { before: 100 }, children: [new TextRun("避免使用 shell=True，将命令和参数作为列表传递：")] }),
            new Paragraph({ spacing: { before: 100, after: 100 }, shading: { fill: "f5f5f5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: "result = subprocess.check_output([\"ping\", \"-n\", \"3\", ip], shell=False, timeout=30)", font: "Courier New", size: 20 })] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 输入验证")] }),
            new Paragraph({ spacing: { before: 100 }, children: [new TextRun("严格验证 IP 地址格式，只允许有效的 IP 地址：")] }),
            new Paragraph({ spacing: { before: 100, after: 100 }, shading: { fill: "f5f5f5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: "import ipaddress; ipaddress.ip_address(ip)  # 验证IP格式", font: "Courier New", size: 20 })] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 使用白名单")] }),
            new Paragraph({ spacing: { before: 100 }, children: [new TextRun("限制可执行的字符，只允许数字和点：")] }),
            new Paragraph({ spacing: { before: 100, after: 100 }, shading: { fill: "f5f5f5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: "allowed_chars = set('0123456789.')  # 白名单字符", font: "Courier New", size: 20 })] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.4 使用专业库")] }),
            new Paragraph({ spacing: { before: 100 }, children: [new TextRun("使用专门的 ping 库替代系统命令：")] }),
            new Paragraph({ spacing: { before: 100, after: 100 }, shading: { fill: "f5f5f5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: "from pythonping import ping; response = ping(ip, count=3)", font: "Courier New", size: 20 })] }),

            // 六、安全建议
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("六、安全建议")] }),
            
            new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "最佳实践：", bold: true })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("永远不要使用 shell=True 执行用户可控的命令")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("对所有用户输入进行严格的格式验证")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("使用白名单而非黑名单进行输入过滤")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("优先使用专门的库而非调用系统命令")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("实施最小权限原则，限制应用程序权限")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun("定期进行安全代码审计和渗透测试")] }),

            // 报告信息
            new Paragraph({ spacing: { before: 400 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "—— 报告完 ——", color: "666666" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 }, children: [new TextRun({ text: "报告生成时间：2026-07-16", size: 20, color: "666666" })] }),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "此报告仅供安全学习和漏洞修复参考，请勿用于非法用途。", size: 20, color: "666666" })] }),
        ]
    }]
});

// 生成文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("C:\\Users\\KQP\\AppData\\Roaming\\TRAE SOLO CN\\ModularData\\ai-agent\\work-mode-projects\\6a5876df7f4af3e9b0599c10\\vulnerability-report-ping.docx", buffer);
    console.log("Word文档已生成: vulnerability-report-ping.docx");
});