/* =========================================================
   API 설정
========================================================= */

const API_BASE_URL =
    window.APP_CONFIG?.API_BASE_URL
    || "http://127.0.0.1:8000";


/* =========================================================
   State
========================================================= */

let currentConversationId = null;

let currentDataItems = [];

let currentChartItems = [];


/* =========================================================
   DOM Elements
========================================================= */

const summaryRms =
    document.getElementById(
        "summary-rms"
    );

const summaryRmsPercentile =
    document.getElementById(
        "summary-rms-percentile"
    );

const summaryTrend3h =
    document.getElementById(
        "summary-trend-3h"
    );

const summaryTrend6h =
    document.getElementById(
        "summary-trend-6h"
    );

const summaryP2p =
    document.getElementById(
        "summary-p2p"
    );

const refreshSummaryButton =
    document.getElementById(
        "refresh-summary-button"
    );


const conversationList =
    document.getElementById(
        "conversation-list"
    );

const newChatButton =
    document.getElementById(
        "new-chat-button"
    );


const chatMessages =
    document.getElementById(
        "chat-messages"
    );

const chatInput =
    document.getElementById(
        "chat-input"
    );

const sendButton =
    document.getElementById(
        "send-button"
    );

const chatLoading =
    document.getElementById(
        "chat-loading"
    );


const addDataButton =
    document.getElementById(
        "add-data-button"
    );

const dataForm =
    document.getElementById(
        "data-form"
    );

const dataId =
    document.getElementById(
        "data-id"
    );

const dataDate =
    document.getElementById(
        "data-date"
    );

const dataValue =
    document.getElementById(
        "data-value"
    );

const dataMemo =
    document.getElementById(
        "data-memo"
    );

const dataP2p =
    document.getElementById(
        "data-p2p"
    );

const dataSampleCount =
    document.getElementById(
        "data-sample-count"
    );

const cancelDataButton =
    document.getElementById(
        "cancel-data-button"
    );

const dataTableBody =
    document.getElementById(
        "data-table-body"
    );


/* =========================================================
   Utility
========================================================= */

function escapeHtml(value) {

    if (
        value === null
        || value === undefined
    ) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatNumber(
    value,
    digits = 4
) {

    const number =
        Number(value);

    if (!Number.isFinite(number)) {
        return "-";
    }

    return number.toFixed(digits);
}


function formatDateTime(value) {

    if (!value) {
        return "-";
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return String(value);
    }

    return date.toLocaleString(
        "ko-KR",
        {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }
    );
}


function formatTrend(trend) {

    if (!trend) {
        return "-";
    }

    const directionMap = {
        increase: "증가",
        decrease: "감소",
        stable: "안정"
    };

    const direction =
        directionMap[
            trend.direction
        ]
        || trend.direction
        || "-";

    const change =
        Number(
            trend.normalized_change_percent
        );

    if (
        !Number.isFinite(change)
    ) {
        return direction;
    }

    const sign =
        change > 0
            ? "+"
            : "";

    return (
        `${direction} `
        + `(${sign}${change.toFixed(2)}%)`
    );
}


/* =========================================================
   Summary
========================================================= */

async function loadSummary() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/data/summary`
            );

        if (!response.ok) {

            throw new Error(
                `Summary API 오류: ${response.status}`
            );
        }

        const summary =
            await response.json();


        summaryRms.textContent =
            formatNumber(
                summary?.rms?.latest,
                4
            );


        const rmsPercentile =
            Number(
                summary?.rms
                    ?.percentile_rank
            );

        summaryRmsPercentile.textContent =
            Number.isFinite(
                rmsPercentile
            )
                ? `${rmsPercentile.toFixed(2)}%`
                : "-";


        summaryTrend3h.textContent =
            formatTrend(
                summary?.trend
                    ?.short_term_3h
            );


        summaryTrend6h.textContent =
            formatTrend(
                summary?.trend
                    ?.mid_term_6h
            );


        const latestP2p =
            Number(
                summary
                    ?.peak_to_peak
                    ?.latest
            );

        const p2pPercentile =
            Number(
                summary
                    ?.peak_to_peak
                    ?.percentile_rank
            );


        if (
            Number.isFinite(
                latestP2p
            )
        ) {

            summaryP2p.textContent =
                Number.isFinite(
                    p2pPercentile
                )
                    ? (
                        `${latestP2p.toFixed(4)} `
                        + `(${p2pPercentile.toFixed(2)}%)`
                    )
                    : latestP2p.toFixed(4);

        } else {

            summaryP2p.textContent =
                "-";
        }

    } catch (error) {

        console.error(
            "Summary 로딩 오류:",
            error
        );

        summaryRms.textContent =
            "오류";

        summaryRmsPercentile.textContent =
            "오류";

        summaryTrend3h.textContent =
            "오류";

        summaryTrend6h.textContent =
            "오류";

        summaryP2p.textContent =
            "오류";
    }
}


/* =========================================================
   RMS Chart
========================================================= */

function drawRmsChart(items) {

    currentChartItems =
        Array.isArray(items)
            ? items
            : [];


    const canvas =
        document.getElementById(
            "rms-chart"
        );

    const emptyMessage =
        document.getElementById(
            "chart-empty-message"
        );


    if (!canvas) {
        return;
    }


    const context =
        canvas.getContext("2d");


    const sortedItems =
        [...currentChartItems]
            .filter(
                item => {

                    const date =
                        new Date(
                            item.date
                        );

                    const value =
                        Number(
                            item.value
                        );

                    return (
                        !Number.isNaN(
                            date.getTime()
                        )
                        &&
                        Number.isFinite(
                            value
                        )
                    );
                }
            )
            .sort(
                (a, b) =>
                    new Date(a.date)
                    -
                    new Date(b.date)
            );


    if (
        sortedItems.length === 0
    ) {

        const rect =
            canvas.getBoundingClientRect();

        context.clearRect(
            0,
            0,
            rect.width,
            rect.height
        );

        emptyMessage
            ?.classList
            .remove("hidden");

        return;
    }


    emptyMessage
        ?.classList
        .add("hidden");


    const container =
        canvas.parentElement;


    const width =
        Math.max(
            container.clientWidth,
            300
        );


    const height =
        Math.max(
            container.clientHeight,
            260
        );


    const pixelRatio =
        window.devicePixelRatio
        || 1;


    canvas.width =
        Math.floor(
            width * pixelRatio
        );

    canvas.height =
        Math.floor(
            height * pixelRatio
        );


    canvas.style.width =
        `${width}px`;

    canvas.style.height =
        `${height}px`;


    context.setTransform(
        pixelRatio,
        0,
        0,
        pixelRatio,
        0,
        0
    );


    const values =
        sortedItems.map(
            item =>
                Number(item.value)
        );


    const padding = {
        top: 24,
        right: 28,
        bottom: 55,
        left: 62
    };


    const chartWidth =
        width
        - padding.left
        - padding.right;


    const chartHeight =
        height
        - padding.top
        - padding.bottom;


    let minValue =
        Math.min(...values);

    let maxValue =
        Math.max(...values);


    if (
        minValue === maxValue
    ) {

        minValue -= 0.5;
        maxValue += 0.5;
    }


    const originalRange =
        maxValue - minValue;


    minValue -=
        originalRange * 0.08;

    maxValue +=
        originalRange * 0.08;


    context.clearRect(
        0,
        0,
        width,
        height
    );


    drawChartGrid(
        context,
        width,
        height,
        padding,
        minValue,
        maxValue
    );


    drawChartLine(
        context,
        sortedItems,
        chartWidth,
        chartHeight,
        padding,
        minValue,
        maxValue
    );


    drawChartDateLabels(
        context,
        sortedItems,
        width,
        height,
        padding
    );


    drawLatestPoint(
        context,
        sortedItems,
        chartWidth,
        chartHeight,
        padding,
        minValue,
        maxValue
    );
}


function drawChartGrid(
    context,
    width,
    height,
    padding,
    minValue,
    maxValue
) {

    const chartHeight =
        height
        - padding.top
        - padding.bottom;


    const gridCount = 5;


    context.font =
        "12px sans-serif";

    context.textAlign =
        "right";

    context.textBaseline =
        "middle";


    for (
        let i = 0;
        i <= gridCount;
        i++
    ) {

        const ratio =
            i / gridCount;


        const y =
            padding.top
            + ratio
            * chartHeight;


        const value =
            maxValue
            -
            ratio
            *
            (
                maxValue
                - minValue
            );


        context.beginPath();

        context.moveTo(
            padding.left,
            y
        );

        context.lineTo(
            width
            - padding.right,
            y
        );

        context.strokeStyle =
            "#e2e8f0";

        context.lineWidth = 1;

        context.stroke();


        context.fillStyle =
            "#64748b";

        context.fillText(
            value.toFixed(2),
            padding.left - 10,
            y
        );
    }


    context.beginPath();

    context.moveTo(
        padding.left,
        padding.top
    );

    context.lineTo(
        padding.left,
        height
        - padding.bottom
    );

    context.lineTo(
        width
        - padding.right,
        height
        - padding.bottom
    );

    context.strokeStyle =
        "#94a3b8";

    context.lineWidth = 1;

    context.stroke();
}


function drawChartLine(
    context,
    items,
    chartWidth,
    chartHeight,
    padding,
    minValue,
    maxValue
) {

    context.beginPath();


    items.forEach(
        (item, index) => {

            const value =
                Number(
                    item.value
                );


            const xRatio =
                items.length === 1
                    ? 0
                    : (
                        index
                        /
                        (
                            items.length
                            - 1
                        )
                    );


            const x =
                padding.left
                +
                xRatio
                * chartWidth;


            const y =
                padding.top
                +
                (
                    (
                        maxValue
                        - value
                    )
                    /
                    (
                        maxValue
                        - minValue
                    )
                )
                *
                chartHeight;


            if (
                index === 0
            ) {

                context.moveTo(
                    x,
                    y
                );

            } else {

                context.lineTo(
                    x,
                    y
                );
            }
        }
    );


    context.strokeStyle =
        "#2563eb";

    context.lineWidth = 2;

    context.lineJoin =
        "round";

    context.lineCap =
        "round";

    context.stroke();
}


function drawLatestPoint(
    context,
    items,
    chartWidth,
    chartHeight,
    padding,
    minValue,
    maxValue
) {

    if (
        items.length === 0
    ) {
        return;
    }


    const latest =
        items[
            items.length - 1
        ];


    const value =
        Number(
            latest.value
        );


    const x =
        padding.left
        + chartWidth;


    const y =
        padding.top
        +
        (
            (
                maxValue
                - value
            )
            /
            (
                maxValue
                - minValue
            )
        )
        *
        chartHeight;


    context.beginPath();

    context.arc(
        x,
        y,
        5,
        0,
        Math.PI * 2
    );

    context.fillStyle =
        "#2563eb";

    context.fill();


    context.beginPath();

    context.arc(
        x,
        y,
        9,
        0,
        Math.PI * 2
    );

    context.strokeStyle =
        "rgba(37, 99, 235, 0.25)";

    context.lineWidth = 4;

    context.stroke();
}


function drawChartDateLabels(
    context,
    items,
    width,
    height,
    padding
) {

    const chartWidth =
        width
        - padding.left
        - padding.right;


    const labelCount =
        Math.min(
            5,
            items.length
        );


    context.font =
        "11px sans-serif";

    context.fillStyle =
        "#64748b";

    context.textAlign =
        "center";

    context.textBaseline =
        "top";


    for (
        let i = 0;
        i < labelCount;
        i++
    ) {

        const ratio =
            labelCount === 1
                ? 0
                : (
                    i
                    /
                    (
                        labelCount
                        - 1
                    )
                );


        const index =
            Math.round(
                ratio
                *
                (
                    items.length
                    - 1
                )
            );


        const item =
            items[index];


        const x =
            padding.left
            +
            ratio
            * chartWidth;


        const date =
            new Date(
                item.date
            );


        const month =
            String(
                date.getMonth() + 1
            )
            .padStart(
                2,
                "0"
            );


        const day =
            String(
                date.getDate()
            )
            .padStart(
                2,
                "0"
            );


        const hour =
            String(
                date.getHours()
            )
            .padStart(
                2,
                "0"
            );


        const minute =
            String(
                date.getMinutes()
            )
            .padStart(
                2,
                "0"
            );


        const label =
            `${month}/${day} ${hour}:${minute}`;


        context.fillText(
            label,
            x,
            height
            - padding.bottom
            + 14
        );
    }
}


/* =========================================================
   Conversation UI
========================================================= */

function addMessage(
    role,
    content
) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        role === "user"
            ? "message user-message"
            : "message assistant-message";


    const roleElement =
        document.createElement(
            "div"
        );


    roleElement.className =
        "message-role";


    roleElement.textContent =
        role === "user"
            ? "사용자"
            : "AI";


    const contentElement =
        document.createElement(
            "div"
        );


    contentElement.className =
        "message-content";


    contentElement.textContent =
        content;


    message.appendChild(
        roleElement
    );

    message.appendChild(
        contentElement
    );


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;
}


function clearChatMessages() {

    chatMessages.innerHTML = "";
}


function startNewConversation() {

    currentConversationId =
        null;


    clearChatMessages();


    addMessage(
        "assistant",
        "새 대화를 시작합니다. "
        + "교반구동장치의 현재 진동 데이터에 대해 질문해 주세요."
    );


    chatInput.value = "";


    renderConversationActiveState();


    chatInput.focus();
}


function setChatLoading(
    loading
) {

    if (loading) {

        chatLoading.classList
            .remove("hidden");

        sendButton.disabled =
            true;

        chatInput.disabled =
            true;

    } else {

        chatLoading.classList
            .add("hidden");

        sendButton.disabled =
            false;

        chatInput.disabled =
            false;
    }
}


/* =========================================================
   AI Chat
========================================================= */

async function sendChatMessage() {

    const message =
        chatInput.value.trim();


    if (!message) {
        return;
    }


    addMessage(
        "user",
        message
    );


    chatInput.value = "";


    setChatLoading(
        true
    );


    try {

        const payload = {
            message: message
        };


        if (
            currentConversationId
        ) {

            payload.conversation_id =
                currentConversationId;
        }


        const response =
            await fetch(
                `${API_BASE_URL}/api/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();

            throw new Error(
                errorText
                ||
                `Chat API 오류: ${response.status}`
            );
        }


        const result =
            await response.json();


        const answer =
            result.answer
            ??
            result.response
            ??
            result.message
            ??
            result.content
            ??
            "AI 응답을 확인할 수 없습니다.";


        currentConversationId =
            result.conversation_id
            ??
            result.conversationId
            ??
            currentConversationId;


        addMessage(
            "assistant",
            answer
        );


        await loadConversationList();

    } catch (error) {

        console.error(
            "Chat 오류:",
            error
        );


        addMessage(
            "assistant",
            "AI 응답을 가져오는 중 오류가 발생했습니다. "
            + "잠시 후 다시 시도해 주세요."
        );

    } finally {

        setChatLoading(
            false
        );


        chatInput.focus();
    }
}


/* =========================================================
   Conversation API
========================================================= */

async function loadConversationList() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/conversations/`
            );


        if (!response.ok) {

            throw new Error(
                `Conversation API 오류: ${response.status}`
            );
        }


        const result =
            await response.json();


        const conversations =
            Array.isArray(result)
                ? result
                : (
                    result.conversations
                    ??
                    result.items
                    ??
                    []
                );


        conversationList.innerHTML =
            "";


        if (
            conversations.length === 0
        ) {

            conversationList.innerHTML =
                `
                <p class="empty-message">
                    저장된 대화가 없습니다.
                </p>
                `;

            return;
        }


        conversations.sort(
            (a, b) => {

                const aDate =
                    new Date(
                        a.updated_at
                        ??
                        a.created_at
                        ??
                        0
                    );


                const bDate =
                    new Date(
                        b.updated_at
                        ??
                        b.created_at
                        ??
                        0
                    );


                return (
                    bDate - aDate
                );
            }
        );


        conversations.forEach(
            conversation => {

                const id =
                    conversation.id
                    ??
                    conversation.conversation_id;


                if (!id) {
                    return;
                }


                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "conversation-item";


                button.dataset.id =
                    id;


                const title =
                    conversation.title
                    ??
                    getConversationTitle(
                        conversation
                    );


                const created =
                    conversation.updated_at
                    ??
                    conversation.created_at;


                button.innerHTML =
                    `
                    <span class="conversation-title">
                        ${escapeHtml(title)}
                    </span>

                    <span class="conversation-date">
                        ${escapeHtml(formatDateTime(created))}
                    </span>
                    `;


                button.addEventListener(
                    "click",
                    () =>
                        loadConversation(
                            id
                        )
                );


                conversationList.appendChild(
                    button
                );
            }
        );


        renderConversationActiveState();

    } catch (error) {

        console.error(
            "대화 목록 오류:",
            error
        );


        conversationList.innerHTML =
            `
            <p class="empty-message">
                대화 목록을 불러오지 못했습니다.
            </p>
            `;
    }
}


function getConversationTitle(
    conversation
) {

    const messages =
        conversation.messages;


    if (
        Array.isArray(messages)
    ) {

        const userMessage =
            messages.find(
                item =>
                    item.role === "user"
            );


        if (
            userMessage?.content
        ) {

            return (
                userMessage.content
                    .slice(0, 30)
            );
        }
    }


    return "AI 대화";
}


async function loadConversation(
    conversationId
) {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/conversations/${conversationId}`
            );


        if (!response.ok) {

            throw new Error(
                `Conversation 조회 오류: ${response.status}`
            );
        }


        const conversation =
            await response.json();


        currentConversationId =
            conversationId;


        clearChatMessages();


        const messages =
            conversation.messages
            ??
            conversation.data?.messages
            ??
            [];


        if (
            messages.length === 0
        ) {

            addMessage(
                "assistant",
                "저장된 메시지가 없습니다."
            );

        } else {

            messages.forEach(
                item => {

                    if (
                        item.role === "system"
                    ) {
                        return;
                    }


                    addMessage(
                        item.role === "user"
                            ? "user"
                            : "assistant",
                        item.content
                        ?? ""
                    );
                }
            );
        }


        renderConversationActiveState();

    } catch (error) {

        console.error(
            "대화 불러오기 오류:",
            error
        );


        alert(
            "대화를 불러오지 못했습니다."
        );
    }
}


function renderConversationActiveState() {

    const buttons =
        document.querySelectorAll(
            ".conversation-item"
        );


    buttons.forEach(
        button => {

            if (
                button.dataset.id
                === currentConversationId
            ) {

                button.classList.add(
                    "active"
                );

            } else {

                button.classList.remove(
                    "active"
                );
            }
        }
    );
}


/* =========================================================
   Data API
========================================================= */

async function loadData() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/data`
            );


        if (!response.ok) {

            throw new Error(
                `Data API 오류: ${response.status}`
            );
        }


        const result =
            await response.json();


        const items =
            Array.isArray(result)
                ? result
                : (
                    result.items
                    ??
                    result.data
                    ??
                    []
                );


        currentDataItems =
            items;


        /*
         * 그래프는 오래된 시간 → 최신 시간
         */
        drawRmsChart(
            items
        );


        /*
         * 표는 최신 데이터가 위로 오도록 정렬
         */
        const tableItems =
            [...items].sort(
                (a, b) =>
                    new Date(b.date)
                    -
                    new Date(a.date)
            );


        renderDataTable(
            tableItems
        );

    } catch (error) {

        console.error(
            "데이터 로딩 오류:",
            error
        );


        dataTableBody.innerHTML =
            `
            <tr>
                <td
                    colspan="6"
                    class="table-empty"
                >
                    데이터를 불러오지 못했습니다.
                </td>
            </tr>
            `;


        drawRmsChart(
            []
        );
    }
}


/* =========================================================
   Data Table
========================================================= */

function renderDataTable(
    items
) {

    dataTableBody.innerHTML =
        "";


    if (
        items.length === 0
    ) {

        dataTableBody.innerHTML =
            `
            <tr>
                <td
                    colspan="6"
                    class="table-empty"
                >
                    등록된 데이터가 없습니다.
                </td>
            </tr>
            `;

        return;
    }


    items.forEach(
        item => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML =
                `
                <td>
                    ${escapeHtml(formatDateTime(item.date))}
                </td>

                <td>
                    ${escapeHtml(formatNumber(item.value, 4))}
                </td>

                <td>
                    ${escapeHtml(formatNumber(item.peak_to_peak, 4))}
                </td>

                <td>
                    ${escapeHtml(item.sample_count ?? "-")}
                </td>

                <td>
                    ${escapeHtml(item.memo ?? "")}
                </td>

                <td>
                    <button
                        type="button"
                        class="table-button edit-button"
                    >
                        수정
                    </button>

                    <button
                        type="button"
                        class="table-button delete-button"
                    >
                        삭제
                    </button>
                </td>
                `;


            const editButton =
                row.querySelector(
                    ".edit-button"
                );


            const deleteButton =
                row.querySelector(
                    ".delete-button"
                );


            editButton.addEventListener(
                "click",
                () =>
                    openEditForm(
                        item
                    )
            );


            deleteButton.addEventListener(
                "click",
                () =>
                    deleteData(
                        item.id
                    )
            );


            dataTableBody.appendChild(
                row
            );
        }
    );
}


/* =========================================================
   Data Form
========================================================= */

function openAddForm() {

    dataForm.reset();

    dataId.value = "";


    dataMemo.value =
        "교반구동장치 진동 측정";


    dataForm.classList
        .remove("hidden");


    dataDate.focus();
}


function openEditForm(
    item
) {

    dataId.value =
        item.id
        ?? "";


    dataDate.value =
        toDateTimeLocal(
            item.date
        );


    dataValue.value =
        item.value
        ?? "";


    dataMemo.value =
        item.memo
        ?? "";


    dataP2p.value =
        item.peak_to_peak
        ?? "";


    dataSampleCount.value =
        item.sample_count
        ?? "";


    dataForm.classList
        .remove("hidden");


    dataForm.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function closeDataForm() {

    dataForm.reset();

    dataId.value = "";


    dataForm.classList
        .add("hidden");
}


function toDateTimeLocal(
    value
) {

    if (!value) {
        return "";
    }


    const date =
        new Date(value);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "";
    }


    const pad =
        number =>
            String(number)
                .padStart(
                    2,
                    "0"
                );


    return (
        `${date.getFullYear()}-`
        + `${pad(date.getMonth() + 1)}-`
        + `${pad(date.getDate())}`
        + `T${pad(date.getHours())}:`
        + `${pad(date.getMinutes())}`
    );
}


/* =========================================================
   Save Data
========================================================= */

async function saveData(
    event
) {

    event.preventDefault();


    const id =
        dataId.value.trim();


    const value =
        Number(
            dataValue.value
        );


    if (
        !dataDate.value
        ||
        !Number.isFinite(value)
    ) {

        alert(
            "측정 일시와 RMS 값을 확인해 주세요."
        );

        return;
    }


    const payload = {

        date:
            new Date(
                dataDate.value
            )
            .toISOString(),

        value:
            value,

        memo:
            dataMemo.value.trim()
            || "교반구동장치 진동 측정"
    };


    if (
        dataP2p.value !== ""
    ) {

        payload.peak_to_peak =
            Number(
                dataP2p.value
            );
    }


    if (
        dataSampleCount.value
        !== ""
    ) {

        payload.sample_count =
            Number(
                dataSampleCount.value
            );
    }


    const url =
        id
            ? (
                `${API_BASE_URL}/api/data/${id}`
            )
            : (
                `${API_BASE_URL}/api/data`
            );


    const method =
        id
            ? "PUT"
            : "POST";


    try {

        const response =
            await fetch(
                url,
                {
                    method: method,

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            payload
                        )
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            throw new Error(
                errorText
                ||
                `저장 오류: ${response.status}`
            );
        }


        closeDataForm();


        /*
         * CRUD 직후 데이터 / Summary / 그래프 갱신
         */
        await Promise.all([
            loadData(),
            loadSummary()
        ]);

    } catch (error) {

        console.error(
            "데이터 저장 오류:",
            error
        );


        alert(
            "데이터 저장 중 오류가 발생했습니다."
        );
    }
}


/* =========================================================
   Delete Data
========================================================= */

async function deleteData(
    id
) {

    if (!id) {

        alert(
            "데이터 ID를 확인할 수 없습니다."
        );

        return;
    }


    const confirmed =
        window.confirm(
            "이 데이터를 삭제하시겠습니까?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/api/data/${id}`,
                {
                    method: "DELETE"
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            throw new Error(
                errorText
                ||
                `삭제 오류: ${response.status}`
            );
        }


        /*
         * 삭제 직후 Summary / Table / Chart 갱신
         */
        await Promise.all([
            loadData(),
            loadSummary()
        ]);

    } catch (error) {

        console.error(
            "데이터 삭제 오류:",
            error
        );


        alert(
            "데이터 삭제 중 오류가 발생했습니다."
        );
    }
}


/* =========================================================
   Event Listeners
========================================================= */

refreshSummaryButton
    ?.addEventListener(
        "click",
        async () => {

            await Promise.all([
                loadSummary(),
                loadData()
            ]);
        }
    );


newChatButton
    ?.addEventListener(
        "click",
        startNewConversation
    );


sendButton
    ?.addEventListener(
        "click",
        sendChatMessage
    );


chatInput
    ?.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
                &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendChatMessage();
            }
        }
    );


addDataButton
    ?.addEventListener(
        "click",
        openAddForm
    );


cancelDataButton
    ?.addEventListener(
        "click",
        closeDataForm
    );


dataForm
    ?.addEventListener(
        "submit",
        saveData
    );


/* =========================================================
   Responsive Chart
========================================================= */

let resizeTimer = null;


window.addEventListener(
    "resize",
    () => {

        clearTimeout(
            resizeTimer
        );


        resizeTimer =
            setTimeout(
                () => {

                    if (
                        currentChartItems
                            .length
                        > 0
                    ) {

                        drawRmsChart(
                            currentChartItems
                        );
                    }

                },
                150
            );
    }
);


/* =========================================================
   Initial Load
========================================================= */

async function initializeApp() {

    await Promise.all([
        loadSummary(),
        loadConversationList(),
        loadData()
    ]);
}


initializeApp();