// API Base URL
const API_BASE = '/api/v1';

// 상태 관리
let currentUser = null;
let accessToken = null;
let refreshToken = null;
let currentPostId = null;
let currentDate = new Date();
let markDates = [];
let selectedDate = null;
let selectedWeekStart = null;
let selectedWeekEnd = null;
const imageUrlCache = new Map();
let currentQuoteId = null;
let bookmarkData = [];
let bookmarkPage = 1;
let bookmarkPageSize = 5;
function isAuthed() {
    return !!accessToken;
}

async function fetchPostImageUrl(postId) {
    if (imageUrlCache.has(postId)) return imageUrlCache.get(postId);
    try {
        const resp = await fetch(`${API_BASE}/posts/image/${postId}`, {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        if (!resp.ok) return null;
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        imageUrlCache.set(postId, url);
        return url;
    } catch (_) {
        return null;
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', async () => {
    // 로컬 스토리지에서 토큰 확인
    const storedToken = localStorage.getItem('access_token');
    const storedRefreshToken = localStorage.getItem('refresh_token');
    
    if (storedToken) {
        accessToken = storedToken;
        refreshToken = storedRefreshToken;
        await checkAuthAndLoad();
    } else {
        showNotAuthed();
        await loadPublicData();
    }
});

// 공개 데이터 로드 (로그인 없이)
async function loadPublicData() {
    await loadQuoteForNotAuth();
    await loadQuestionForNotAuth();
}

// 인증 확인 및 데이터 로드
async function checkAuthAndLoad() {
    try {
        const response = await fetch(`${API_BASE}/users/me`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            const userData = await response.json();
            currentUser = userData;
            showAuthed();
            await loadAllData();
        } else if (response.status === 401) {
            // 토큰 만료 시 갱신 시도
            await attemptTokenRefresh();
        } else {
            throw new Error('인증 실패');
        }
    } catch (error) {
        console.error('인증 확인 실패:', error);
        showNotAuthed();
    }
}

// 토큰 갱신 시도
async function attemptTokenRefresh() {
    try {
        const response = await fetch(`${API_BASE}/users/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                refresh_token: refreshToken
            })
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            await checkAuthAndLoad();
        } else {
            throw new Error('토큰 갱신 실패');
        }
    } catch (error) {
        console.error('토큰 갱신 실패:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        showNotAuthed();
    }
}

// 인증된 페이지 표시
function showAuthed() {
    document.getElementById('not-authed').classList.add('hidden');
    document.getElementById('authed').classList.remove('hidden');
    document.getElementById('username-display').textContent = currentUser.username;
    renderCalendar();
}

// 인증되지 않은 페이지 표시
function showNotAuthed() {
    document.getElementById('not-authed').classList.remove('hidden');
    document.getElementById('authed').classList.add('hidden');
}

// 로그인/회원가입 탭 전환
function showLogin() {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.tab-btn').classList.add('active');
    document.getElementById('login-form').classList.add('active');
    document.getElementById('register-form').classList.remove('active');
    clearErrors();
}

function showRegister() {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('register-form').classList.add('active');
    clearErrors();
}

function clearErrors() {
    document.getElementById('login-error').textContent = '';
    document.getElementById('register-error').textContent = '';
}

// 회원가입
async function handleRegister() {
    const username = document.getElementById('register-username').value;
    const loginId = document.getElementById('register-login-id').value;
    const password = document.getElementById('register-password').value;

    if (!username || !loginId || !password) {
        showError('register-error', '모든 필드를 입력해주세요.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/users/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                login_id: loginId,
                password
            })
        });

        if (response.ok) {
            showLogin();
            showError('login-error', '회원가입이 완료되었습니다. 로그인해주세요.');
        } else {
            const error = await response.json();
            showError('register-error', error.detail || '회원가입에 실패했습니다.');
        }
    } catch (error) {
        showError('register-error', '회원가입 중 오류가 발생했습니다.');
    }
}

// 로그인
async function handleLogin() {
    const loginId = document.getElementById('login-id').value;
    const password = document.getElementById('login-password').value;

    if (!loginId || !password) {
        showError('login-error', '아이디와 비밀번호를 입력해주세요.');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('username', loginId);
        formData.append('password', password);

        const response = await fetch(`${API_BASE}/users/login`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            accessToken = data.access_token;
            refreshToken = data.refresh_token;
            localStorage.setItem('access_token', accessToken);
            localStorage.setItem('refresh_token', refreshToken);
            
            await checkAuthAndLoad();
        } else {
            const error = await response.json();
            showError('login-error', error.detail || '로그인에 실패했습니다.');
        }
    } catch (error) {
        showError('login-error', '로그인 중 오류가 발생했습니다.');
    }
}

// 로그아웃
function handleLogout() {
    accessToken = null;
    refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    showNotAuthed();
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
    }
}

// 모든 데이터 로드
async function loadAllData() {
    await Promise.all([
        loadQuote(),
        loadQuestion(),
        loadCalendar(),
        loadDiaryList(),
        loadBookmarksData()
    ]);
    // 로그인 기본 화면: 오늘이 포함된 주 요약 표시 및 주 하이라이트
    try {
        await selectDate(new Date());
    } catch (_) {}
    // 명언 하트 상태 동기화
    updateBookmarkButton();
}

// 명언 로드 (인증된 상태)
async function loadQuote() {
    try {
        const response = await fetch(`${API_BASE}/quotes/`);
        if (response.ok) {
            const quote = await response.json();
            const textEl = document.getElementById('quote-banner-text');
            const authorEl = document.getElementById('quote-banner-author');
            if (textEl && authorEl) {
                textEl.textContent = `"${quote.message}"`;
                authorEl.textContent = `- ${quote.author}`;
            }
            currentQuoteId = quote?.id ?? null;
            updateBookmarkButton();
        }
    } catch (error) {
        console.error('명언 로드 실패:', error);
    }
}

// 명언 로드 (로그인하지 않은 상태)
async function loadQuoteForNotAuth() {
    try {
        const response = await fetch(`${API_BASE}/quotes/`);
        if (response.ok) {
            const quote = await response.json();
            const textEl = document.getElementById('quote-banner-text-not-auth');
            const authorEl = document.getElementById('quote-banner-author-not-auth');
            if (textEl && authorEl) {
                textEl.textContent = `"${quote.message}"`;
                authorEl.textContent = `- ${quote.author}`;
            }
            // 비로그인 시엔 북마크 불가
            currentQuoteId = null;
            updateBookmarkButton();
        }
    } catch (error) {
        console.error('명언 로드 실패:', error);
    }
}

// 명언 새로고침
async function refreshQuote() {
    // 상태에 따라 분기
    const isAuthedVisible = !document.getElementById('authed').classList.contains('hidden');
    if (isAuthedVisible) {
        await loadQuote();
    } else {
        await loadQuoteForNotAuth();
    }
}

// 현재 명언 북마크 추가
async function bookmarkCurrentQuote() {
    if (!currentQuoteId || !isAuthed()) return;
    try {
        const already = isCurrentQuoteBookmarked();
        const method = already ? 'DELETE' : 'POST';
        const resp = await fetch(`${API_BASE}/quotes/bookmark/${currentQuoteId}`, {
            method,
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            alert(err.detail || '요청에 실패했습니다.');
            return;
        }
        await loadBookmarksData();
        updateBookmarkButton();
    } catch (e) {
        console.error(e);
        alert('요청에 실패했습니다.');
    }
}

function isCurrentQuoteBookmarked() {
    if (!currentQuoteId) return false;
    return bookmarkData.some(b => b.id === currentQuoteId);
}

function updateBookmarkButton() {
    const btn = document.getElementById('bookmark-banner-btn');
    if (!btn) return;
    if (!isAuthed() || !currentQuoteId) {
        btn.textContent = '♡';
        btn.title = '로그인 필요';
        btn.style.opacity = '0.6';
        btn.style.cursor = 'not-allowed';
        return;
    }
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
    if (isCurrentQuoteBookmarked()) {
        btn.textContent = '❤';
        btn.title = '북마크 취소';
    } else {
        btn.textContent = '♡';
        btn.title = '북마크 추가';
    }
}

// 질문 로드 (인증된 상태)
async function loadQuestion() {
    try {
        const response = await fetch(`${API_BASE}/questions/`);
        if (response.ok) {
            const question = await response.json();
            document.getElementById('question-message').textContent = question.message;
        }
    } catch (error) {
        console.error('질문 로드 실패:', error);
    }
}

// 질문 로드 (로그인하지 않은 상태)
async function loadQuestionForNotAuth() {
    try {
        const response = await fetch(`${API_BASE}/questions/`);
        if (response.ok) {
            const question = await response.json();
            document.getElementById('question-message-not-auth').textContent = question.message;
        }
    } catch (error) {
        console.error('질문 로드 실패:', error);
    }
}

// 질문 새로고침
async function refreshQuestion() {
    await loadQuestion();
}

// 북마크 토글
async function toggleBookmark() {
    try {
        const quoteMessage = document.getElementById('quote-message').textContent;
        // 여기서는 간단하게 구현하지만, 실제로는 quote_id를 저장해야 함
        // 현재 임시 구현
    } catch (error) {
        console.error('북마크 실패:', error);
    }
}

// 북마크 보기
async function showBookmarks() {
    try {
        const response = await fetch(`${API_BASE}/quotes/bookmarks/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            const bookmarks = await response.json();
            const container = document.getElementById('bookmark-list-container');
            container.innerHTML = '';

            bookmarks.forEach(bookmark => {
                const item = document.createElement('div');
                item.className = 'bookmark-item';
                item.innerHTML = `
                    <div class="bookmark-item-content">"${bookmark.message}"</div>
                    <div class="bookmark-item-author">- ${bookmark.author}</div>
                    <div class="bookmark-item-actions">
                        <button onclick="deleteBookmark(${bookmark.id})" class="secondary-btn">삭제</button>
                    </div>
                `;
                container.appendChild(item);
            });

            switchToMode('bookmark');
        }
    } catch (error) {
        console.error('북마크 로드 실패:', error);
    }
}

// 북마크 사이드바 데이터 로드
async function loadBookmarksData() {
    try {
        const response = await fetch(`${API_BASE}/quotes/bookmarks/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });
        if (!response.ok) return;
        bookmarkData = await response.json();
        bookmarkPage = 1;
        renderBookmarksSidebar();
        // 명언 하트 상태 동기화 (bookmarkData 의존)
        updateBookmarkButton();
    } catch (e) {
        console.error('북마크 로드 실패:', e);
    }
}

function renderBookmarksSidebar() {
    const listEl = document.getElementById('bookmark-sidebar-list');
    const pageInfo = document.getElementById('bm-page-info');
    if (!listEl || !pageInfo) return;

    const total = bookmarkData.length;
    const totalPages = Math.max(1, Math.ceil(total / bookmarkPageSize));
    if (bookmarkPage > totalPages) bookmarkPage = totalPages;
    if (bookmarkPage < 1) bookmarkPage = 1;

    const start = (bookmarkPage - 1) * bookmarkPageSize;
    const end = start + bookmarkPageSize;
    const pageItems = bookmarkData.slice(start, end);

    listEl.innerHTML = '';
    pageItems.forEach(b => {
        const item = document.createElement('div');
        item.className = 'bookmark-item';
        item.innerHTML = `
            <div class="bookmark-item-content">"${b.message}"</div>
            <div class="bookmark-item-author">- ${b.author}</div>
            <div class="bookmark-item-actions">
                <button class="secondary-btn" onclick="deleteBookmarkAndRefresh(${b.id})">삭제</button>
            </div>
        `;
        listEl.appendChild(item);
    });

    pageInfo.textContent = `${bookmarkPage} / ${totalPages}`;
}

function changeBookmarkPage(delta) {
    bookmarkPage += delta;
    renderBookmarksSidebar();
}

async function deleteBookmarkAndRefresh(quoteId) {
    await deleteBookmark(quoteId);
    await loadBookmarksData();
}

// 북마크 닫기
function closeBookmarks() {
    switchToMode('list');
}

// 북마크 삭제
async function deleteBookmark(quoteId) {
    try {
        const response = await fetch(`${API_BASE}/quotes/bookmark/${quoteId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            // 기존 모드 갱신
            showBookmarks();
            // 사이드바 갱신
            loadBookmarksData();
        }
    } catch (error) {
        console.error('북마크 삭제 실패:', error);
    }
}

// 캘린더 로드
async function loadCalendar() {
    try {
        const response = await fetch(`${API_BASE}/users/calender`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            const data = await response.json();
            markDates = data.map(item => new Date(item.date));
            renderCalendar();
            updateCalendarButton(false);
        }
    } catch (error) {
        console.error('캘린더 로드 실패:', error);
    }
}

// 캘린더 렌더링
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    document.getElementById('current-month-display').textContent = 
        `${year}년 ${month + 1}월`;

    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    // 월요일 시작으로 변경
    const startDate = new Date(firstDay);
    const firstDayOfWeek = startDate.getDay();
    const mondayOffset = firstDayOfWeek === 0 ? -6 : 1 - firstDayOfWeek;
    startDate.setDate(startDate.getDate() + mondayOffset);
    
    const endDate = new Date(lastDay);
    const lastDayOfWeek = endDate.getDay();
    const sundayOffset = lastDayOfWeek === 0 ? 0 : 7 - lastDayOfWeek;
    endDate.setDate(endDate.getDate() + sundayOffset);
    
    const today = new Date();
    const todayStart = new Date(today);
    todayStart.setHours(0,0,0,0);
    
    const container = document.getElementById('calendar-grid');
    container.innerHTML = '';
    
    const currentDateIter = new Date(startDate);
    
    while (currentDateIter <= endDate) {
        const day = currentDateIter.getDate();
        const isOtherMonth = currentDateIter.getMonth() !== month;
        
        // 미래 날짜 제외
        const dateToCheck = new Date(currentDateIter);
        dateToCheck.setHours(0,0,0,0);
        const isFuture = dateToCheck.getTime() > todayStart.getTime();
        
        const hasEntry = markDates.some(markDate => 
            markDate.toDateString() === currentDateIter.toDateString()
        );
        const isToday = currentDateIter.toDateString() === today.toDateString();
        
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        if (isOtherMonth || isFuture) dayElement.classList.add('other-month');
        if (hasEntry) dayElement.classList.add('has-entry');
        if (isToday) dayElement.classList.add('today');
        if (selectedWeekStart && selectedWeekEnd) {
            const iterDateOnly = new Date(currentDateIter.getTime());
            iterDateOnly.setHours(0,0,0,0);
            const weekStartOnly = new Date(selectedWeekStart.getTime());
            weekStartOnly.setHours(0,0,0,0);
            const weekEndOnly = new Date(selectedWeekEnd.getTime());
            weekEndOnly.setHours(0,0,0,0);
            
            // 주 범위 체크: 시작일 <= 현재날짜 <= 종료일
            if (iterDateOnly.getTime() >= weekStartOnly.getTime() && 
                iterDateOnly.getTime() <= weekEndOnly.getTime()) {
                dayElement.classList.add('in-selected-week');
            }
        }
        if (selectedDate && currentDateIter.toDateString() === selectedDate.toDateString()) {
            dayElement.classList.add('selected-date');
        }
        
        dayElement.innerHTML = `
            <div class="day-number">${day}</div>
            ${hasEntry ? '<div class="day-indicator"></div>' : ''}
        `;
        
        const dateForClick = new Date(currentDateIter);
        dayElement.onclick = () => {
            if (!isOtherMonth && !isFuture) {
                selectDate(dateForClick);
            }
        };
        
        container.appendChild(dayElement);
        currentDateIter.setDate(currentDateIter.getDate() + 1);
    }
}

// 월 변경
function changeMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);
    renderCalendar();
}

// 날짜 선택
async function selectDate(date) {
    const formattedDate = date.toISOString().split('T')[0];
    document.getElementById('diary-date').value = formattedDate;
    
    selectedDate = new Date(date);
    selectedDate.setHours(0,0,0,0);
    
    // 주 계산 (월요일 시작)
    const dayOfWeek = (selectedDate.getDay() + 6) % 7; // 0=월
    selectedWeekStart = new Date(selectedDate);
    selectedWeekStart.setDate(selectedDate.getDate() - dayOfWeek);
    selectedWeekStart.setHours(0,0,0,0);
    selectedWeekEnd = new Date(selectedWeekStart);
    selectedWeekEnd.setDate(selectedWeekStart.getDate() + 6);
    selectedWeekEnd.setHours(0,0,0,0);
    
    // 선택한 날짜에 일기가 있는지 확인
    const hasEntry = markDates.some(markDate => 
        markDate.toDateString() === selectedDate.toDateString()
    );
    updateCalendarButton(hasEntry);
    
    renderCalendar();
    
    // 해당 주의 일기 목록 불러오기
    await loadPostsByWeek(date);
}

// 캘린더 버튼 업데이트
function updateCalendarButton(hasEntry) {
    const btn = document.querySelector('.calendar-section button.primary-btn');
    if (!btn) return;
    
    if (hasEntry && selectedDate) {
        btn.textContent = '일기 보기';
        btn.onclick = () => viewDiaryByDate(selectedDate);
    } else {
        btn.textContent = '새 일기 작성';
        btn.onclick = showNewDiaryForm;
    }
}

// 날짜로 일기 보기
async function viewDiaryByDate(date) {
    try {
        const targetDate = date.toISOString().split('T')[0];
        const response = await fetch(`${API_BASE}/posts/by-week?target_date=${targetDate}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            const posts = await response.json();
            const postForDate = posts.find(p => p.date === targetDate);
            if (postForDate) {
                loadDiaryForView(postForDate);
            }
        }
    } catch (error) {
        console.error('일기 로드 실패:', error);
    }
}

// 일기 목록 로드
async function loadDiaryList() {
    try {
        const response = await fetch(`${API_BASE}/posts/?page=1&limit=100`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            const posts = await response.json();
            const container = document.getElementById('diary-list-container');
            container.innerHTML = '';

            for (const post of posts) {
                const item = document.createElement('div');
                item.className = 'diary-item';
                item.onclick = () => loadDiaryForView(post);
                
                let imageHtml = '';
                if (post.image_url) {
                    const imgUrl = await fetchPostImageUrl(post.id);
                    if (imgUrl) {
                        imageHtml = `<div class="diary-item-thumbnail"><img src="${imgUrl}" alt="Thumbnail"></div>`;
                    }
                }
                
                item.innerHTML = `
                    ${imageHtml}
                    <div class="diary-item-content-wrapper">
                        <div class="diary-item-header">
                            <div class="diary-item-title">${post.title}</div>
                            <div class="diary-item-date">${formatDate(post.date)}</div>
                        </div>
                        <div class="diary-item-preview">${post.content}</div>
                    </div>
                `;
                container.appendChild(item);
            }
        }
    } catch (error) {
        console.error('일기 목록 로드 실패:', error);
    }
}

// 해당 주의 일기 목록 로드
async function loadPostsByWeek(date) {
    try {
        const targetDate = date.toISOString().split('T')[0];
        const response = await fetch(`${API_BASE}/posts/by-week?target_date=${targetDate}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            const posts = await response.json();
            const container = document.getElementById('diary-list-container');
            container.innerHTML = '';

            if (posts.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #888;">이 주에는 작성된 일기가 없습니다.</p>';
                switchToMode('list');
                return;
            }

            for (const post of posts) {
                const item = document.createElement('div');
                item.className = 'diary-item';
                item.onclick = () => loadDiaryForView(post);
                
                let imageHtml = '';
                if (post.image_url) {
                    const imgUrl = await fetchPostImageUrl(post.id);
                    if (imgUrl) {
                        imageHtml = `<div class="diary-item-thumbnail"><img src="${imgUrl}" alt="Thumbnail"></div>`;
                    }
                }
                
                item.innerHTML = `
                    ${imageHtml}
                    <div class="diary-item-content-wrapper">
                        <div class="diary-item-header">
                            <div class="diary-item-title">${post.title}</div>
                            <div class="diary-item-date">${formatDate(post.date)}</div>
                        </div>
                        <div class="diary-item-preview">${post.content}</div>
                    </div>
                `;
                container.appendChild(item);
            }

            switchToMode('list');
        }
    } catch (error) {
        console.error('주별 일기 로드 실패:', error);
    }
}

// 일기 편집을 위해 로드
async function loadDiaryForEdit(post) {
    currentPostId = post.id;
    document.getElementById('diary-date').value = post.date;
    document.getElementById('diary-title').value = post.title;
    document.getElementById('diary-content').value = post.content;
    document.getElementById('delete-btn').classList.remove('hidden');
    
    // 이미지 로드
    const preview = document.getElementById('image-preview');
    preview.innerHTML = '';
    if (post.image_url) {
        const imgUrl = await fetchPostImageUrl(post.id);
        if (imgUrl) {
            const img = document.createElement('img');
            img.src = imgUrl;
            preview.appendChild(img);
        }
    }
    
    switchToMode('edit');
}

// 일기 보기 모드 로드
async function loadDiaryForView(post) {
    currentPostId = post.id;
    document.getElementById('view-title').textContent = post.title;
    document.getElementById('view-date').textContent = formatDate(post.date);
    const viewImage = document.getElementById('view-image');
    viewImage.innerHTML = '';
    if (post.image_url) {
        const imgUrl = await fetchPostImageUrl(post.id);
        if (imgUrl) {
            const img = document.createElement('img');
            img.src = imgUrl;
            viewImage.appendChild(img);
        }
    }
    document.getElementById('view-content').textContent = post.content;
    switchToMode('view');
}

function enterEditFromView() {
    if (!currentPostId) return;
    // 보기에서 편집으로 전환을 위해 목록에서 해당 데이터 다시 사용
    const dateText = document.getElementById('view-date').textContent;
    document.getElementById('diary-date').value = dateText;
    document.getElementById('diary-title').value = document.getElementById('view-title').textContent;
    document.getElementById('diary-content').value = document.getElementById('view-content').textContent;
    document.getElementById('delete-btn').classList.remove('hidden');
    switchToMode('edit');
}

// 새 일기 작성 폼 표시
function showNewDiaryForm() {
    currentPostId = null;
    const dateInput = document.getElementById('diary-date');
    const today = new Date();
    const selected = selectedDate ? new Date(selectedDate) : today;
    // 작성 가능 여부 확인
    if (!isDateWritable(selected)) {
        alert('선택한 날짜에는 일기를 작성할 수 없습니다.');
        return;
    }
    dateInput.max = formatDate(today);
    dateInput.value = formatDate(selected);
    document.getElementById('diary-title').value = '';
    const editor = document.getElementById('diary-content');
    editor.value = '';
    // 질문을 placeholder로 설정
    fetch(`${API_BASE}/questions/`).then(async (res) => {
        if (!res.ok) return;
        const q = await res.json();
        const hint = q.message;
        editor.placeholder = hint || '오늘은 어떤 하루였나요?';
    }).catch(() => { editor.placeholder = '오늘은 어떤 하루였나요?'; });
    document.getElementById('image-preview').innerHTML = '';
    document.getElementById('delete-btn').classList.add('hidden');
    document.getElementById('diary-image').value = '';
    switchToMode('edit');
}

function isDateWritable(date) {
    const todayOnly = new Date();
    todayOnly.setHours(0,0,0,0);
    const cmp = new Date(date);
    cmp.setHours(0,0,0,0);
    // 미래 불가
    if (cmp > todayOnly) return false;
    // 이미 작성된 날 불가
    const exists = markDates.some(d => d.toDateString() === cmp.toDateString());
    if (exists) return false;
    return true;
}

// 일기 저장
async function saveDiary() {
    const date = document.getElementById('diary-date').value;
    const title = document.getElementById('diary-title').value;
    const content = document.getElementById('diary-content').value;
    const imageFile = document.getElementById('diary-image').files[0];
    
    if (!title || !content) {
        alert('제목과 내용을 입력해주세요.');
        return;
    }

    try {
        let post;
        
        if (currentPostId) {
            // 수정
            const formData = new FormData();
            formData.append('post_data', JSON.stringify({ title, content }));
            if (imageFile) {
                formData.append('image_file', imageFile);
            }
            
            const response = await fetch(`${API_BASE}/posts/${currentPostId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: formData
            });

            if (response.ok) {
                post = await response.json();
            } else {
                throw new Error('일기 수정 실패');
            }
        } else {
            // 생성
            const formData = new FormData();
            formData.append('title', title);
            formData.append('date', date);
            formData.append('content', content);
            
            const response = await fetch(`${API_BASE}/posts/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: formData
            });

            if (response.ok) {
                post = await response.json();
                
                // 이미지 업로드
                if (imageFile) {
                    await uploadImage(post.id, imageFile);
                }
            } else {
                throw new Error('일기 생성 실패');
            }
        }
        
        await loadCalendar();
        await loadDiaryList();
        switchToMode('list');
    } catch (error) {
        console.error('일기 저장 실패:', error);
        alert('일기 저장에 실패했습니다.');
    }
}

// 이미지 업로드
async function uploadImage(postId, imageFile) {
    try {
        const formData = new FormData();
        formData.append('image_file', imageFile);
        
        const response = await fetch(`${API_BASE}/posts/${postId}/image`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('이미지 업로드 실패');
        }
    } catch (error) {
        console.error('이미지 업로드 실패:', error);
    }
}

// 일기 삭제
async function deleteDiary() {
    if (!currentPostId) return;
    
    if (!confirm('정말 이 일기를 삭제하시겠습니까?')) return;

    try {
        const response = await fetch(`${API_BASE}/posts/${currentPostId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            }
        });

        if (response.ok) {
            await loadCalendar();
            await loadDiaryList();
            switchToMode('list');
        } else {
            throw new Error('일기 삭제 실패');
        }
    } catch (error) {
        console.error('일기 삭제 실패:', error);
        alert('일기 삭제에 실패했습니다.');
    }
}

// 일기 취소
function cancelDiary() {
    switchToMode('list');
}

// 모드 전환
function switchToMode(mode) {
    // 모든 모드 숨기기
    document.getElementById('diary-edit-mode').classList.add('hidden');
    document.getElementById('diary-list-mode').classList.add('hidden');
    document.getElementById('bookmark-mode').classList.add('hidden');
    document.getElementById('diary-view-mode').classList.add('hidden');
    
    // 선택한 모드 표시
    if (mode === 'edit') {
        document.getElementById('diary-edit-mode').classList.remove('hidden');
    } else if (mode === 'list') {
        document.getElementById('diary-list-mode').classList.remove('hidden');
    } else if (mode === 'bookmark') {
        document.getElementById('bookmark-mode').classList.remove('hidden');
    } else if (mode === 'view') {
        document.getElementById('diary-view-mode').classList.remove('hidden');
    }
}

// 날짜 포맷
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// 이미지 미리보기
document.getElementById('diary-image').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
});

