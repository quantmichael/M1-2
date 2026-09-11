const API_BASE_URL = "http://127.0.0.1:8000";

let currentConversationId = null;
let editingDataId = null;


/* =============================
   Summary
============================= */

function formatTrend(direction) {

    if (direction === "increase") {
        return "증가";
    }

    if (direction === "decrease") {
        return "감소";
    }

    return "안정";
}


async function loadSummary() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/data/summary`
        );

        if (!response.ok) {
            throw new Error(
                "Summary API 호출에 실패했습니다."
            );
        }

        const data = await response.json();

        document.getElementById(
            "summary-rms"
        ).textContent =
            data.rms.latest;

        document.getElementById(
            "summary-rms-percentile"
        ).textContent =
            `${data.rms.percentile_rank} 백분위`;

        document.getElementById(
            "summary-trend-3h"
        ).textContent =
            formatTrend(
                data.trend.short_term_3h.direction
            );

        document.getElementById(
            "summary-trend-6h"
        ).textContent =
            formatTrend(
                data.trend.mid_term_6h.direction
            );

        document.getElementById(
            "summary-p2p"
        ).textContent =
            data.peak_to_peak.latest;

    } catch (error) {

        console.error(
            "Summary 로딩 오류:",
            error
        );

    }

}


/* =============================
   Chat
============================= */

function addMessage(role, text) {

    const chatMessages =
        document.getElementById(
            "chat-messages"
        );

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add(
        "message",
        role
    );

    messageDiv.textContent = text;

    chatMessages.appendChild(
        messageDiv
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;

    return messageDiv;
}


function startNewConversation() {

    currentConversationId = null;

    const chatMessages =
        document.getElementById(
            "chat-messages"
        );

    chatMessages.innerHTML = "";

    addMessage(
        "assistant",
        "새로운 대화를 시작합니다. 진동 데이터에 대해 질문해주세요."
    );

    document.getElementById(
        "chat-input"
    ).focus();

}


async function sendChatMessage() {

    const input =
        document.getElementById(
            "chat-input"
        );

    const sendButton =
        document.getElementById(
            "send-button"
        );

    const message =
        input.value.trim();

    if (!message) {
        return;
    }

    addMessage(
        "user",
        message
    );

    input.value = "";
    sendButton.disabled = true;

    const loadingMessage =
        addMessage(
            "assistant",
            "분석 중..."
        );

    try {

        const requestBody = {
            message: message
        };

        if (currentConversationId) {

            requestBody.conversation_id =
                currentConversationId;

        }

        const response = await fetch(
            `${API_BASE_URL}/api/chat/`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    requestBody
                )
            }
        );

        if (!response.ok) {

            throw new Error(
                "Chat API 호출에 실패했습니다."
            );

        }

        const data =
            await response.json();

        loadingMessage.remove();

        addMessage(
            "assistant",
            data.answer
        );

        currentConversationId =
            data.conversation_id;

        await loadConversationList();

    } catch (error) {

        console.error(
            "Chat 오류:",
            error
        );

        loadingMessage.remove();

        addMessage(
            "assistant",
            "AI 응답을 불러오지 못했습니다."
        );

    } finally {

        sendButton.disabled = false;
        input.focus();

    }

}


/* =============================
   Conversations
============================= */

async function loadConversationList() {

    const conversationList =
        document.getElementById(
            "conversation-list"
        );

    conversationList.innerHTML =
        "대화를 불러오는 중...";

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/conversations/`
        );

        if (!response.ok) {

            throw new Error(
                "대화 목록 API 호출에 실패했습니다."
            );

        }

        const conversations =
            await response.json();

        conversationList.innerHTML = "";

        if (conversations.length === 0) {

            conversationList.innerHTML =
                '<p class="empty-message">저장된 대화가 없습니다.</p>';

            return;
        }

        conversations.forEach(
            (conversation) => {

                const button =
                    document.createElement(
                        "button"
                    );

                button.classList.add(
                    "conversation-item"
                );

                button.textContent =
                    conversation.title;

                button.addEventListener(
                    "click",
                    () => {

                        loadConversation(
                            conversation.id
                        );

                    }
                );

                conversationList.appendChild(
                    button
                );

            }
        );

    } catch (error) {

        console.error(
            "대화 목록 로딩 오류:",
            error
        );

        conversationList.innerHTML =
            '<p class="empty-message">대화 목록을 불러오지 못했습니다.</p>';

    }

}


async function loadConversation(
    conversationId
) {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/conversations/${conversationId}`
        );

        if (!response.ok) {

            throw new Error(
                "대화를 불러오지 못했습니다."
            );

        }

        const data =
            await response.json();

        const chatMessages =
            document.getElementById(
                "chat-messages"
            );

        chatMessages.innerHTML = "";

        data.messages.forEach(
            (message) => {

                addMessage(
                    message.role,
                    message.content
                );

            }
        );

        currentConversationId =
            data.id;

    } catch (error) {

        console.error(
            "대화 로딩 오류:",
            error
        );

    }

}


/* =============================
   Data CRUD
============================= */

async function loadData() {

    const tableBody =
        document.getElementById(
            "data-table-body"
        );

    tableBody.innerHTML =
        '<tr><td colspan="6">데이터를 불러오는 중...</td></tr>';

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/data/`
        );

        if (!response.ok) {

            throw new Error(
                "데이터 조회 실패"
            );

        }

        const items =
            await response.json();

        items.sort(
            (a, b) => new Date(b.date) - new Date(a.date)
        );
        
        tableBody.innerHTML = "";

        if (items.length === 0) {

            tableBody.innerHTML =
                '<tr><td colspan="6">저장된 데이터가 없습니다.</td></tr>';

            return;
        }

        items.forEach(
            (item) => {

                const row =
                    document.createElement(
                        "tr"
                    );

                row.innerHTML = `
                    <td>${item.date}</td>
                    <td>${item.value}</td>
                    <td>${item.memo ?? ""}</td>
                    <td>${item.peak_to_peak ?? "-"}</td>
                    <td>${item.sample_count ?? "-"}</td>
                    <td>
                        <button class="edit-button">
                            수정
                        </button>

                        <button class="delete-button">
                            삭제
                        </button>
                    </td>
                `;

                row.querySelector(
                    ".edit-button"
                ).addEventListener(
                    "click",
                    () => openEditForm(item)
                );

                row.querySelector(
                    ".delete-button"
                ).addEventListener(
                    "click",
                    () => deleteData(item.id)
                );

                tableBody.appendChild(
                    row
                );

            }
        );

    } catch (error) {

        console.error(
            "데이터 로딩 오류:",
            error
        );

        tableBody.innerHTML =
            '<tr><td colspan="6">데이터를 불러오지 못했습니다.</td></tr>';

    }

}


function openAddForm() {

    editingDataId = null;

    document.getElementById(
        "data-form"
    ).classList.remove(
        "hidden"
    );

    document.getElementById(
        "data-date"
    ).value = "";

    document.getElementById(
        "data-value"
    ).value = "";

    document.getElementById(
        "data-memo"
    ).value = "";

    document.getElementById(
        "data-p2p"
    ).value = "";

    document.getElementById(
        "data-sample-count"
    ).value = "";

}


function openEditForm(item) {

    editingDataId =
        item.id;

    document.getElementById(
        "data-form"
    ).classList.remove(
        "hidden"
    );

    document.getElementById(
        "data-date"
    ).value =
        item.date.substring(0, 16);

    document.getElementById(
        "data-value"
    ).value =
        item.value;

    document.getElementById(
        "data-memo"
    ).value =
        item.memo ?? "";

    document.getElementById(
        "data-p2p"
    ).value =
        item.peak_to_peak ?? "";

    document.getElementById(
        "data-sample-count"
    ).value =
        item.sample_count ?? "";

}


function closeDataForm() {

    editingDataId = null;

    document.getElementById(
        "data-form"
    ).classList.add(
        "hidden"
    );

}


async function saveData() {

    const date =
        document.getElementById(
            "data-date"
        ).value;

    const value =
        document.getElementById(
            "data-value"
        ).value;

    const memo =
        document.getElementById(
            "data-memo"
        ).value;

    const peakToPeak =
        document.getElementById(
            "data-p2p"
        ).value;

    const sampleCount =
        document.getElementById(
            "data-sample-count"
        ).value;


    if (!date || !value) {

        alert(
            "측정시각과 RMS는 필수입니다."
        );

        return;
    }


    const payload = {
        date: date,
        value: Number(value),
        memo: memo,
        peak_to_peak:
            peakToPeak
                ? Number(peakToPeak)
                : null,
        sample_count:
            sampleCount
                ? Number(sampleCount)
                : null
    };


    let url =
        `${API_BASE_URL}/api/data/`;

    let method =
        "POST";


    if (editingDataId) {

        url =
            `${API_BASE_URL}/api/data/${editingDataId}`;

        method =
            "PUT";

    }


    try {

        const response = await fetch(
            url,
            {
                method: method,

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    payload
                )
            }
        );


        if (!response.ok) {

            throw new Error(
                "데이터 저장 실패"
            );

        }


        closeDataForm();

        await loadData();

        await loadSummary();


    } catch (error) {

        console.error(
            "데이터 저장 오류:",
            error
        );

        alert(
            "데이터 저장에 실패했습니다."
        );

    }

}


async function deleteData(id) {

    const confirmed =
        confirm(
            "이 데이터를 삭제하시겠습니까?"
        );

    if (!confirmed) {
        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/api/data/${id}`,
            {
                method:
                    "DELETE"
            }
        );


        if (!response.ok) {

            throw new Error(
                "데이터 삭제 실패"
            );

        }


        await loadData();

        await loadSummary();


    } catch (error) {

        console.error(
            "데이터 삭제 오류:",
            error
        );

        alert(
            "데이터 삭제에 실패했습니다."
        );

    }

}


/* =============================
   Events
============================= */

document.getElementById(
    "send-button"
).addEventListener(
    "click",
    sendChatMessage
);


document.getElementById(
    "chat-input"
).addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {
            sendChatMessage();
        }

    }
);


document.getElementById(
    "new-chat-button"
).addEventListener(
    "click",
    startNewConversation
);


document.getElementById(
    "add-data-button"
).addEventListener(
    "click",
    openAddForm
);


document.getElementById(
    "save-data-button"
).addEventListener(
    "click",
    saveData
);


document.getElementById(
    "cancel-data-button"
).addEventListener(
    "click",
    closeDataForm
);


/* =============================
   Initial Load
============================= */

loadSummary();
loadConversationList();
loadData();