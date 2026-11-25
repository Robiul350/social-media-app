(() => {
    "use strict";

    const body = document.body;
    const root = document.documentElement;
    const dashboardDataElement = document.getElementById("sc-dashboard-data");
    const analyticsDataElement = document.getElementById("sc-analytics-data");

    const readJSON = (element) => {
        if (!element) return null;
        try {
            return JSON.parse(element.textContent);
        } catch (error) {
            return null;
        }
    };

    const isDark = () => root.dataset.scAdminTheme === "dark";

    const basePalette = {
        navy: "#172554",
        blue: "#2563EB",
        violet: "#8B5CF6",
        teal: "#0D9488",
        amber: "#F59E0B",
        success: "#16A34A",
        danger: "#DC2626",
    };

    const palette = () => ({
        ...basePalette,
        grid: isDark() ? "#253657" : "#E2E8F0",
        axis: isDark() ? "#9AA8C0" : "#64748B",
        canvas: isDark() ? "#111B33" : "#FFFFFF",
        blue: isDark() ? "#60A5FA" : "#2563EB",
        violet: isDark() ? "#A78BFA" : "#8B5CF6",
        teal: isDark() ? "#2DD4BF" : "#0D9488",
        amber: isDark() ? "#FBBF24" : "#F59E0B",
    });

    const hexToRgba = (hex, alpha) => {
        const clean = String(hex).replace("#", "");
        const full = clean.length === 3 ? clean.split("").map((c) => c + c).join("") : clean;
        const value = Number.parseInt(full, 16);
        const red = (value >> 16) & 255;
        const green = (value >> 8) & 255;
        const blueChannel = value & 255;
        return `rgba(${red}, ${green}, ${blueChannel}, ${alpha})`;
    };

    const setTheme = (theme) => {
        const next = theme === "dark" ? "dark" : "light";
        root.dataset.scAdminTheme = next;
        try {
            localStorage.setItem("sc-admin-theme", next);
        } catch (error) {
            /* Storage can be unavailable in private browsing. */
        }
        const toggle = document.getElementById("sc-theme-toggle");
        if (toggle) {
            toggle.setAttribute("aria-pressed", String(next === "dark"));
            toggle.setAttribute("aria-label", next === "dark" ? "Switch to light theme" : "Switch to dark theme");
        }
        let meta = document.querySelector('meta[name="theme-color"]');
        if (!meta) {
            meta = document.createElement("meta");
            meta.setAttribute("name", "theme-color");
            document.head.appendChild(meta);
        }
        meta.setAttribute("content", next === "dark" ? "#0B1220" : "#172554");
        window.dispatchEvent(new Event("sc-theme-changed"));
    };

    const themeToggle = document.getElementById("sc-theme-toggle");
    if (themeToggle) {
        themeToggle.setAttribute("aria-pressed", String(isDark()));
        themeToggle.setAttribute("aria-label", isDark() ? "Switch to light theme" : "Switch to dark theme");
        themeToggle.addEventListener("click", () => setTheme(isDark() ? "light" : "dark"));
    }

    const mobileToggle = document.getElementById("sc-mobile-nav-toggle");
    if (mobileToggle) {
        mobileToggle.addEventListener("click", () => {
            const isOpen = body.classList.toggle("sc-nav-open");
            mobileToggle.setAttribute("aria-expanded", String(isOpen));
            mobileToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
            if (isOpen) {
                document.querySelector("#nav-sidebar .sc-sidebar-link")?.focus();
            }
        });

        document.addEventListener("click", (event) => {
            if (
                body.classList.contains("sc-nav-open") &&
                !event.target.closest("#nav-sidebar") &&
                !event.target.closest("#sc-mobile-nav-toggle")
            ) {
                body.classList.remove("sc-nav-open");
                mobileToggle.setAttribute("aria-expanded", "false");
                mobileToggle.setAttribute("aria-label", "Open navigation");
            }
        });
    }

    const sidebarToggles = Array.from(document.querySelectorAll("[data-sc-sidebar-toggle]"));
    const setCollapsed = (collapsed) => {
        body.classList.toggle("sc-sidebar-collapsed", collapsed);
        sidebarToggles.forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(!collapsed));
            toggle.setAttribute("aria-label", collapsed ? "Expand navigation" : "Collapse navigation");
            toggle.title = collapsed ? "Expand navigation" : "Collapse navigation";
        });
        try {
            localStorage.setItem("sc-admin-sidebar-collapsed", String(collapsed));
        } catch (error) {
            /* Storage can be unavailable in private browsing. */
        }
    };
    if (sidebarToggles.length && window.innerWidth > 900) {
        let storedCollapsed = false;
        try {
            storedCollapsed = localStorage.getItem("sc-admin-sidebar-collapsed") === "true";
        } catch (error) {
            storedCollapsed = false;
        }
        setCollapsed(storedCollapsed);
        sidebarToggles.forEach((toggle) => {
            toggle.addEventListener("click", () => {
                setCollapsed(!body.classList.contains("sc-sidebar-collapsed"));
            });
        });
    }

    const navFilter = document.getElementById("nav-filter");
    if (navFilter) {
        navFilter.addEventListener("input", () => {
            const term = navFilter.value.trim().toLowerCase();
            document.querySelectorAll("#nav-sidebar .sc-sidebar-group").forEach((group) => {
                let visibleItems = 0;
                group.querySelectorAll("li").forEach((item) => {
                    const matches = !term || (item.textContent || "").toLowerCase().includes(term);
                    item.hidden = !matches;
                    if (matches) visibleItems += 1;
                });
                group.hidden = visibleItems === 0;
            });
        });
        navFilter.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && navFilter.value) {
                navFilter.value = "";
                navFilter.dispatchEvent(new Event("input"));
            }
        });
    }

    document.querySelectorAll("[data-search-form]").forEach((form) => {
        const scope = form.querySelector("[data-search-scope]");
        const input = form.querySelector('input[name="q"]');
        const toggle = form.querySelector(".sc-search-toggle");
        if (!scope || !input) return;

        const applyScope = () => {
            form.action = scope.value;
            input.placeholder = `Search ${scope.options[scope.selectedIndex].text.toLowerCase()}...`;
        };
        applyScope();
        scope.addEventListener("change", () => {
            applyScope();
            input.focus();
        });

        if (toggle) {
            toggle.addEventListener("click", () => {
                const isOpen = form.classList.toggle("is-open");
                toggle.setAttribute("aria-expanded", String(isOpen));
                toggle.setAttribute("aria-label", isOpen ? "Close search" : "Open search");
                if (isOpen) input.focus();
            });
            document.addEventListener("click", (event) => {
                if (form.classList.contains("is-open") && !form.contains(event.target)) {
                    form.classList.remove("is-open");
                    toggle.setAttribute("aria-expanded", "false");
                    toggle.setAttribute("aria-label", "Open search");
                }
            });
            document.addEventListener("keydown", (event) => {
                if (event.key === "Escape" && form.classList.contains("is-open")) {
                    form.classList.remove("is-open");
                    toggle.setAttribute("aria-expanded", "false");
                    toggle.setAttribute("aria-label", "Open search");
                    toggle.focus();
                }
            });
        }
    });

    /* Reusable confirmation modal for explicit administrative actions. */
    const confirmModal = document.getElementById("sc-confirm-modal");
    let pendingConfirmation = null;

    const closeConfirm = () => {
        if (!confirmModal || confirmModal.hidden) return;
        confirmModal.hidden = true;
        body.classList.remove("sc-modal-open");
        pendingConfirmation = null;
    };

    if (confirmModal) {
        confirmModal.querySelectorAll("[data-sc-confirm-dismiss]").forEach((button) => {
            button.addEventListener("click", closeConfirm);
        });
        confirmModal.querySelector("[data-sc-confirm-accept]")?.addEventListener("click", () => {
            const action = pendingConfirmation;
            closeConfirm();
            if (typeof action === "function") action();
        });
        document.querySelectorAll("[data-sc-confirm]").forEach((trigger) => {
            trigger.addEventListener("click", (event) => {
                event.preventDefault();
                pendingConfirmation = () => {
                    if (trigger.form) trigger.form.submit();
                    else if (trigger.tagName === "A") window.location.assign(trigger.href);
                };
                const message = confirmModal.querySelector("#sc-confirm-message");
                if (message) message.textContent = trigger.dataset.scConfirm || "Please confirm this action.";
                confirmModal.hidden = false;
                body.classList.add("sc-modal-open");
                confirmModal.querySelector("[data-sc-confirm-accept]")?.focus();
            });
        });
    }

    /* Django messages become restrained toast cards without changing their content. */
    document.querySelectorAll(".messagelist li").forEach((message) => {
        if (message.dataset.scToast) return;
        message.dataset.scToast = "true";
        message.classList.add("sc-toast");
        message.setAttribute("role", message.classList.contains("error") ? "alert" : "status");
        const close = document.createElement("button");
        close.type = "button";
        close.className = "sc-toast-close";
        close.setAttribute("aria-label", "Dismiss message");
        close.textContent = "×";
        close.addEventListener("click", () => message.remove());
        message.appendChild(close);
        if (!message.classList.contains("error")) {
            window.setTimeout(() => {
                if (message.isConnected) message.remove();
            }, 6500);
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        if (confirmModal && !confirmModal.hidden) {
            closeConfirm();
            return;
        }
        if (body.classList.contains("sc-nav-open") && mobileToggle) {
            body.classList.remove("sc-nav-open");
            mobileToggle.setAttribute("aria-expanded", "false");
            mobileToggle.setAttribute("aria-label", "Open navigation");
            mobileToggle.focus();
        }
    });

    /* Chart rendering: smooth lines, grouped bars, donuts, and hover tooltips. */
    const chartState = new WeakMap();
    const boundCanvases = new WeakSet();
    let tooltip = null;

    const getTooltip = () => {
        if (!tooltip) {
            tooltip = document.createElement("div");
            tooltip.className = "sc-chart-tooltip";
            tooltip.hidden = true;
            document.body.appendChild(tooltip);
        }
        return tooltip;
    };

    const showTooltip = (event, title, rows) => {
        const element = getTooltip();
        element.textContent = "";
        const heading = document.createElement("strong");
        heading.textContent = title;
        element.appendChild(heading);
        rows.forEach((row) => {
            const line = document.createElement("span");
            const dot = document.createElement("i");
            dot.style.background = row.color;
            const label = document.createElement("span");
            label.textContent = `${row.label}: ${row.value}`;
            line.append(dot, label);
            element.appendChild(line);
        });
        element.hidden = false;
        const left = Math.min(event.clientX + window.scrollX + 14, window.scrollX + document.documentElement.clientWidth - 190);
        const top = Math.max(window.scrollY + 8, event.clientY + window.scrollY - 12);
        element.style.left = `${Math.max(window.scrollX + 8, left)}px`;
        element.style.top = `${top}px`;
    };

    const hideTooltip = () => {
        if (tooltip) tooltip.hidden = true;
    };

    const bindTooltip = (canvas, resolver) => {
        if (boundCanvases.has(canvas)) return;
        boundCanvases.add(canvas);
        canvas.addEventListener("mousemove", (event) => {
            const result = resolver(event, canvas);
            if (result) showTooltip(event, result.title, result.rows);
            else hideTooltip();
        });
        canvas.addEventListener("mouseleave", hideTooltip);
    };

    const setupCanvas = (canvas) => {
        const ratio = window.devicePixelRatio || 1;
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;
        if (!width || !height) return null;
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        const context = canvas.getContext("2d");
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
        context.clearRect(0, 0, width, height);
        return { context, width, height };
    };

    const hideSkeleton = (canvas) => {
        const skeleton = canvas.previousElementSibling;
        if (skeleton && skeleton.classList.contains("sc-chart-skeleton")) skeleton.hidden = true;
    };

    const drawEmpty = (canvas, setup) => {
        hideSkeleton(canvas);
        const { context: ctx, width, height } = setup;
        ctx.fillStyle = palette().axis;
        ctx.font = "600 12px Inter, Segoe UI, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("No data for this range", width / 2, height / 2);
        chartState.delete(canvas);
    };

    const drawGrid = (ctx, width, height, padding, maximum, colors) => {
        const plotHeight = height - padding.top - padding.bottom;
        ctx.font = "10px Inter, Segoe UI, sans-serif";
        ctx.textAlign = "right";
        ctx.textBaseline = "middle";
        for (let step = 0; step <= 4; step += 1) {
            const y = padding.top + (plotHeight * step) / 4;
            ctx.beginPath();
            ctx.strokeStyle = colors.grid;
            ctx.moveTo(padding.left, y);
            ctx.lineTo(width - padding.right, y);
            ctx.stroke();
            ctx.fillStyle = colors.axis;
            ctx.fillText(String(Math.round((maximum * (4 - step)) / 4)), padding.left - 8, y);
        }
    };

    const drawXLabels = (ctx, labels, pointX, width, height, padding) => {
        const step = Math.max(1, Math.ceil(labels.length / 7));
        ctx.font = "9px Inter, Segoe UI, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillStyle = palette().axis;
        labels.forEach((label, index) => {
            if (index % step === 0 || index === labels.length - 1) {
                const x = Math.min(width - padding.right - 12, Math.max(padding.left + 10, pointX(index)));
                ctx.fillText(String(label), x, height - padding.bottom + 10);
            }
        });
    };

    const drawSmoothPath = (ctx, points) => {
        if (!points.length) return;
        ctx.moveTo(points[0].x, points[0].y);
        for (let index = 1; index < points.length; index += 1) {
            const previous = points[index - 1];
            const current = points[index];
            const middle = (previous.x + current.x) / 2;
            ctx.bezierCurveTo(middle, previous.y, middle, current.y, current.x, current.y);
        }
    };

    const drawLineChart = (canvas, data, series) => {
        const setup = setupCanvas(canvas);
        if (!setup || !data || !Array.isArray(data.labels)) return;
        const { context: ctx, width, height } = setup;
        const colors = palette();
        const padding = { left: 40, right: 16, top: 18, bottom: 32 };
        const plotWidth = width - padding.left - padding.right;
        const plotHeight = height - padding.top - padding.bottom;
        const labels = data.labels;
        const activeSeries = series.filter(
            (item) => Array.isArray(data[item.key]) && data[item.key].length === labels.length
        );
        const maximum = Math.max(1, ...activeSeries.flatMap((item) => data[item.key]));
        if (!activeSeries.some((item) => data[item.key].some((value) => value > 0))) {
            drawEmpty(canvas, setup);
            return;
        }

        drawGrid(ctx, width, height, padding, maximum, colors);
        const pointX = (index) =>
            labels.length < 2
                ? padding.left + plotWidth / 2
                : padding.left + (plotWidth * index) / (labels.length - 1);
        const pointY = (value) => padding.top + plotHeight - (plotHeight * value) / maximum;
        drawXLabels(ctx, labels, pointX, width, height, padding);

        activeSeries.forEach((item, seriesIndex) => {
            const values = data[item.key];
            const stroke = colors[item.color] || colors.blue;
            const points = values.map((value, index) => ({ x: pointX(index), y: pointY(value), value }));

            if (item.fill && seriesIndex === 0) {
                const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + plotHeight);
                gradient.addColorStop(0, hexToRgba(stroke, isDark() ? 0.24 : 0.16));
                gradient.addColorStop(1, hexToRgba(stroke, 0));
                ctx.beginPath();
                drawSmoothPath(ctx, points);
                ctx.lineTo(points[points.length - 1].x, padding.top + plotHeight);
                ctx.lineTo(points[0].x, padding.top + plotHeight);
                ctx.closePath();
                ctx.fillStyle = gradient;
                ctx.fill();
            }

            ctx.beginPath();
            drawSmoothPath(ctx, points);
            ctx.strokeStyle = stroke;
            ctx.lineWidth = item.width || 2.6;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.stroke();

            const step = Math.max(1, Math.ceil(labels.length / 12));
            points.forEach((point, index) => {
                if (labels.length > 14 && index % step !== 0 && index !== labels.length - 1) return;
                ctx.beginPath();
                ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
                ctx.fillStyle = colors.canvas;
                ctx.fill();
                ctx.lineWidth = 2;
                ctx.strokeStyle = stroke;
                ctx.stroke();
            });
        });

        chartState.set(canvas, {
            type: "line",
            labels,
            series: activeSeries,
            pointX,
            padding,
            width,
        });
        bindTooltip(canvas, (event) => {
            const state = chartState.get(canvas);
            if (!state) return null;
            const rect = canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            if (x < state.padding.left || x > state.width - 16) return null;
            const totalSegments = state.labels.length - 1;
            const ratio = totalSegments <= 0 ? 0 : (x - state.padding.left) / (state.width - state.padding.left - 16);
            const index = Math.max(0, Math.min(state.labels.length - 1, Math.round(ratio * totalSegments)));
            return {
                title: state.labels[index],
                rows: state.series.map((item) => ({
                    label: item.label || item.key,
                    value: data[item.key][index],
                    color: colors[item.color] || colors.blue,
                })),
            };
        });
        hideSkeleton(canvas);
    };

    const roundedRect = (ctx, x, y, width, height, radius) => {
        const r = Math.min(radius, width / 2, Math.abs(height) / 2);
        ctx.beginPath();
        ctx.moveTo(x + r, y);
        ctx.lineTo(x + width - r, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + r);
        ctx.lineTo(x + width, y + height - r);
        ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
        ctx.lineTo(x + r, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - r);
        ctx.lineTo(x, y + r);
        ctx.quadraticCurveTo(x, y, x + r, y);
        ctx.closePath();
    };

    const drawBarChart = (canvas, data, series, labelsKey) => {
        const setup = setupCanvas(canvas);
        if (!setup || !data) return;
        const { context: ctx, width, height } = setup;
        const colors = palette();
        const padding = { left: 40, right: 16, top: 18, bottom: 32 };
        const plotWidth = width - padding.left - padding.right;
        const plotHeight = height - padding.top - padding.bottom;
        const labels = Array.isArray(data[labelsKey]) ? data[labelsKey] : data.labels || [];
        const activeSeries = series.filter((item) => Array.isArray(data[item.key]));
        const maximum = Math.max(1, ...activeSeries.flatMap((item) => data[item.key]));
        if (!activeSeries.some((item) => data[item.key].some((value) => value > 0))) {
            drawEmpty(canvas, setup);
            return;
        }

        drawGrid(ctx, width, height, padding, maximum, colors);
        const band = plotWidth / Math.max(1, labels.length);
        const barWidth = Math.min(22, Math.max(4, (band - 10) / Math.max(1, activeSeries.length)));
        const barPoints = [];

        activeSeries.forEach((item, seriesIndex) => {
            const values = data[item.key];
            const stroke = colors[item.color] || colors.blue;
            values.forEach((value, index) => {
                const center = padding.left + band * index + band / 2;
                const offset = (seriesIndex - (activeSeries.length - 1) / 2) * (barWidth + 3);
                const x = center + offset - barWidth / 2;
                const barHeight = (plotHeight * value) / maximum;
                const y = padding.top + plotHeight - barHeight;
                roundedRect(ctx, x, y, barWidth, Math.max(1, barHeight), Math.min(5, barWidth / 2));
                ctx.fillStyle = stroke;
                ctx.fill();
                barPoints.push({ index, seriesIndex, x, y, width: barWidth, value });
            });
        });

        drawXLabels(
            ctx,
            labels,
            (index) => padding.left + band * index + band / 2,
            width,
            height,
            padding
        );

        chartState.set(canvas, { type: "bar", labels, series: activeSeries, barPoints, padding, width, colors });
        bindTooltip(canvas, (event) => {
            const state = chartState.get(canvas);
            if (!state) return null;
            const rect = canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            const hit = state.barPoints.find(
                (point) => x >= point.x - 3 && x <= point.x + point.width + 3 && y >= point.y
            );
            if (!hit) return null;
            const item = state.series[hit.seriesIndex];
            return {
                title: state.labels[hit.index] || "",
                rows: [{ label: item.label || item.key, value: hit.value, color: state.colors[item.color] || state.colors.blue }],
            };
        });
        hideSkeleton(canvas);
    };

    const drawDonutChart = (canvas, data, valuesKey, labels, colorKeys) => {
        const setup = setupCanvas(canvas);
        if (!setup || !data || !Array.isArray(data[valuesKey])) return;
        const { context: ctx, width, height } = setup;
        const colors = palette();
        const values = data[valuesKey];
        const total = values.reduce((sum, value) => sum + value, 0);
        if (!total) {
            drawEmpty(canvas, setup);
            return;
        }

        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.max(30, Math.min(width, height) / 2 - 22);
        const innerRadius = radius * 0.62;
        const slices = [];
        let angle = -Math.PI / 2;

        values.forEach((value, index) => {
            if (!value) return;
            const sweep = (value / total) * Math.PI * 2;
            const color = colors[colorKeys[index]] || colors.blue;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, angle + 0.015, angle + sweep - 0.015);
            ctx.arc(centerX, centerY, innerRadius, angle + sweep - 0.015, angle + 0.015, true);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();
            slices.push({ start: angle, end: angle + sweep, label: labels[index], value, color });
            angle += sweep;
        });

        ctx.fillStyle = colors.axis;
        ctx.font = "9px Inter, Segoe UI, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("TOTAL", centerX, centerY - 12);
        ctx.fillStyle = isDark() ? "#E8EDF8" : "#0F172A";
        ctx.font = "700 22px Inter, Segoe UI, sans-serif";
        ctx.fillText(String(total), centerX, centerY + 8);

        chartState.set(canvas, { type: "donut", slices, centerX, centerY, radius, innerRadius });
        bindTooltip(canvas, (event) => {
            const state = chartState.get(canvas);
            if (!state) return null;
            const rect = canvas.getBoundingClientRect();
            const dx = event.clientX - rect.left - state.centerX;
            const dy = event.clientY - rect.top - state.centerY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < state.innerRadius || distance > state.radius + 4) return null;
            let pointerAngle = Math.atan2(dy, dx);
            if (pointerAngle < -Math.PI / 2) pointerAngle += Math.PI * 2;
            const slice = state.slices.find(
                (item) => pointerAngle >= item.start && pointerAngle <= item.end
            );
            if (!slice) return null;
            return {
                title: slice.label,
                rows: [{ label: "Total", value: slice.value, color: slice.color }],
            };
        });
        hideSkeleton(canvas);
    };

    const seriesLabels = {
        users: "New users",
        posts: "Posts",
        registrations: "Registrations",
        registrations_cumulative: "Cumulative users",
        active_users: "Active user-days",
        comments: "Comments",
        likes: "Likes",
        friend_requests_created: "Requests created",
        friend_requests_accepted: "Requests accepted",
        reports: "Reports",
        messages: "Messages",
        notifications: "Notifications",
        monthly_active_users: "Monthly active users",
    };

    const canvasSeries = (canvas) => {
        const series = [
            {
                key: canvas.dataset.chartKey,
                label: seriesLabels[canvas.dataset.chartKey] || canvas.dataset.chartKey,
                color: canvas.dataset.chartColor || "blue",
                fill: true,
            },
        ];
        if (canvas.dataset.secondaryKey) {
            series.push({
                key: canvas.dataset.secondaryKey,
                label: seriesLabels[canvas.dataset.secondaryKey] || canvas.dataset.secondaryKey,
                color: canvas.dataset.secondaryColor || "teal",
            });
        }
        if (canvas.dataset.tertiaryKey) {
            series.push({
                key: canvas.dataset.tertiaryKey,
                label: seriesLabels[canvas.dataset.tertiaryKey] || canvas.dataset.tertiaryKey,
                color: canvas.dataset.tertiaryColor || "amber",
            });
        }
        return series.filter((item) => item.key);
    };

    const dashboardData = readJSON(dashboardDataElement);
    const analyticsData = readJSON(analyticsDataElement);

    const renderCharts = () => {
        hideTooltip();
        if (dashboardData) {
            const userCanvas = document.getElementById("sc-user-chart");
            const postCanvas = document.getElementById("sc-post-chart");
            if (userCanvas) {
                drawLineChart(userCanvas, dashboardData, [
                    { key: "users", label: "New users", color: "blue", fill: true, width: 2.8 },
                ]);
            }
            if (postCanvas) {
                drawLineChart(postCanvas, dashboardData, [
                    { key: "posts", label: "New posts", color: "violet", fill: true, width: 2.8 },
                ]);
            }
        }

        if (analyticsData) {
            document.querySelectorAll(".sc-analytics-chart").forEach((canvas) => {
                const type = canvas.dataset.chartType || "line";
                if (type === "donut") {
                    drawDonutChart(
                        canvas,
                        analyticsData,
                        canvas.dataset.valuesKey || "engagement_values",
                        (canvas.dataset.donutLabels || "Series").split(","),
                        (canvas.dataset.donutColors || "blue,violet").split(",")
                    );
                } else if (type === "bar") {
                    drawBarChart(
                        canvas,
                        analyticsData,
                        canvasSeries(canvas),
                        canvas.dataset.labelsKey || "labels"
                    );
                } else {
                    drawLineChart(canvas, analyticsData, canvasSeries(canvas));
                }
            });
        }
    };

    if (dashboardData || analyticsData) {
        renderCharts();
        window.addEventListener("resize", renderCharts);
        window.addEventListener("sc-theme-changed", renderCharts);
    }
})();
