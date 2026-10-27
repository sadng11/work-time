# UI/UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely redesign the work_time application UI/UX with modern Bootstrap RTL layout, FontAwesome 6 icons, clean SaaS aesthetics, and high usability while preserving 100% of existing functionality, Jalali calendar support, and calculations.

**Architecture:** Create a centralized `static/css/custom.css` file defining CSS variables (Design Tokens), card elevation, badge styling, and table ergonomics. Install and bundle FontAwesome 6 locally in `static/` with CDN fallback. Restructure `base.html`, `home.html`, `report.html`, `edit_entry.html`, and `factor.html` to leverage Bootstrap RTL components, FontAwesome icons, and clean responsive layouts.

**Tech Stack:** Django 5.x, Bootstrap RTL 5, FontAwesome 6, Jalali DatePicker, IRANSansWeb(FaNum) font.

**Spec:** `docs/superpowers/specs/2026-10-27-ui-ux-redesign-design.md`

## Global Constraints
- Direction: RTL (`dir="rtl"`, `lang="fa"`)
- Default font: `IRANSansWeb(FaNum)`
- Admin path: `/Sadng1044/`
- Date handling: Jalali format YYYY-MM-DD and `jalalidatepicker`
- Database & calculations: zero changes to ORM duration and financial formulas; preserve all existing URLs and view names.

---

### Task 1: Setup FontAwesome 6 Assets and Create `static/css/custom.css`

**Files:**
- Create: `static/css/custom.css`
- Create/Download: FontAwesome 6 css and webfonts under `static/css/fontawesome.min.css` and `static/webfonts/`
- Test: Check file existence and CSS loading syntax

**Interfaces:**
- Consumes: Existing Bootstrap RTL and IRANSans fonts in `static/`
- Produces: Complete CSS tokens and FontAwesome icon classes for all templates

- [ ] **Step 1: Download or setup FontAwesome 6 assets in `static/`**
Download FontAwesome 6 Free CSS and webfonts into `static/css/fontawesome.min.css` and `static/webfonts/` with CDN fallback URL configured in `base.html`.

- [ ] **Step 2: Create `static/css/custom.css` with Design Tokens, card styles, and animations**
Include CSS variables (`--color-primary`, `--color-bg`, `--color-surface`, etc.), soft glassmorphism, pulse animation for running tasks, rounded cards, buttons, badges, and responsive utilities.

- [ ] **Step 3: Verify static files exist and have non-zero size**
Run check via bash to verify files exist.

- [ ] **Step 4: Commit Task 1**
```bash
git add static/css/custom.css static/css/fontawesome* static/webfonts/ 2>/dev/null || git add static/
git commit -m "feat(ui): add FontAwesome 6 assets and custom design tokens CSS"
```

---

### Task 2: Redesign `timesheet/templates/base.html`

**Files:**
- Modify: `timesheet/templates/base.html`
- Test: Verify page title, navbar links, messages, font loading, script initialization

**Interfaces:**
- Consumes: `static/css/custom.css`, `static/css/bootstrap.min.css`, `static/css/fontawesome.min.css`, `jalalidatepicker`
- Produces: Base layout with top sticky glassmorphic navbar, messages block, container, and footer for all pages

- [ ] **Step 1: Replace `base.html` content with modern layout**
Remove 91KB inline SVG data-uri from `<style>`. Add sticky navbar with logo icon (`fa-solid fa-clock-rotate-left`), navigation links (داشبورد `fa-solid fa-house`, گزارشات `fa-solid fa-chart-pie`, مدیریت `fa-solid fa-sliders`), live today Jalali date widget, user badge, responsive mobile menu toggler, styled dismissible messages, and clean footer.

- [ ] **Step 2: Test rendering with Django test suite**
Run: `docker exec work_time_web python manage.py test timesheet`
Expected: 7 tests pass.

- [ ] **Step 3: Commit Task 2**
```bash
git add timesheet/templates/base.html
git commit -m "feat(ui): redesign base layout with modern navbar and clean styling"
```

---

### Task 3: Redesign `timesheet/templates/home.html`

**Files:**
- Modify: `timesheet/templates/home.html`
- Test: View home template rendering, quick entry submission, manual entry submission, recent entries table

**Interfaces:**
- Consumes: `time_entry_form`, `manual_form`, `projects`, `time_entries`, `start_date`, `end_date` from `views.home`
- Produces: Modern home dashboard with KPI widgets, segmented pill tabs, icon-styled forms, and high-clarity table

- [ ] **Step 1: Implement KPI summary cards at top of `home.html`**
Add 3 cards: Live status (showing whether a project timer is currently active with glowing dot or idle), active project counter (`fa-solid fa-briefcase`), and monthly report quick access (`fa-solid fa-file-invoice-dollar`).

- [ ] **Step 2: Implement segmented pill tabs for Quick Entry and Manual Entry**
Style tabs with `fa-solid fa-bolt-lightning` for quick entry and `fa-solid fa-pen-to-square` for manual entry. Add icons to form field labels, clean inputs, and ergonomically sized submit buttons.

- [ ] **Step 3: Redesign Recent Entries table**
Add FontAwesome icons, status badges (glowing amber for active/unclosed entries `fa-solid fa-stopwatch`, green badge for duration), and clean action buttons (edit `fa-solid fa-pen`, delete `fa-solid fa-trash-can`). Add welcoming Empty State when no entries exist.

- [ ] **Step 4: Verify test suite passes**
Run: `docker exec work_time_web python manage.py test timesheet`
Expected: 7 tests pass.

- [ ] **Step 5: Commit Task 3**
```bash
git add timesheet/templates/home.html
git commit -m "feat(ui): redesign home dashboard with KPI widgets, pill tabs, and modern table"
```

---

### Task 4: Redesign `timesheet/templates/report.html`

**Files:**
- Modify: `timesheet/templates/report.html`
- Test: Check filter form submission, total hours display, table rows, and factor/home action buttons

**Interfaces:**
- Consumes: `daily_report`, `total_hours`, `start`, `end`, `project_id`, `project`, `project_list` from `views.report`
- Produces: Modern filter bar, total hours KPI card, report table, and primary/secondary CTA buttons

- [ ] **Step 1: Redesign filter bar in a card**
Use responsive Bootstrap grid with inputs for start date, end date, project select, and a stylish filter button with `fa-solid fa-filter`.

- [ ] **Step 2: Add Total Working Hours highlight KPI banner**
Display `total_hours` in an eye-catching card with `fa-solid fa-hourglass-half` and Persian formatting.

- [ ] **Step 3: Redesign daily report table and bottom action buttons**
Format columns, row numbers, durations, descriptions, and action buttons. Add Primary CTA for "چاپ فاکتور" (`fa-solid fa-file-invoice-dollar`) and Secondary for "بازگشت به خانه" (`fa-solid fa-house`).

- [ ] **Step 4: Verify test suite passes**
Run: `docker exec work_time_web python manage.py test timesheet`
Expected: 7 tests pass.

- [ ] **Step 5: Commit Task 4**
```bash
git add timesheet/templates/report.html
git commit -m "feat(ui): redesign report page with modern filter bar and KPI summary"
```

---

### Task 5: Redesign `timesheet/templates/edit_entry.html`

**Files:**
- Modify: `timesheet/templates/edit_entry.html`
- Test: Verify edit form display, validation error display, submit and cancel actions

**Interfaces:**
- Consumes: `form`, `entry` from `views.edit_time_entry`
- Produces: Focused center-aligned edit card with styled inputs, helpful hints, and action buttons

- [ ] **Step 1: Redesign `edit_entry.html` with focused card design**
Centered card (`max-width: 650px`), gradient header with `fa-solid fa-pen-to-square`, cleanly spaced fields with icons, Jalali datetime picker triggers, and dual buttons (Save `fa-solid fa-check` and Cancel `fa-solid fa-xmark`).

- [ ] **Step 2: Verify test suite passes**
Run: `docker exec work_time_web python manage.py test timesheet`
Expected: 7 tests pass.

- [ ] **Step 3: Commit Task 5**
```bash
git add timesheet/templates/edit_entry.html
git commit -m "feat(ui): redesign edit entry page with focused card layout"
```

---

### Task 6: Modernize `timesheet/templates/factor.html` Toolbar & Print Media

**Files:**
- Modify: `timesheet/templates/factor.html`
- Test: Check browser toolbar icons, A4 invoice sheet layout, and `@media print` rules

**Interfaces:**
- Consumes: Invoice variables (`total_hours`, `base_fee`, `total_fee`, `string_fee`, `project`, `invoice_number`, `today`) from `views.factor`
- Produces: Elegant printable A4 invoice sheet with FontAwesome toolbar buttons and clean corporate design

- [ ] **Step 1: Modernize top action toolbar**
Replace inline SVG icons with FontAwesome icons: Print (`fa-solid fa-print`), Back to Report (`fa-solid fa-arrow-right`), Dashboard (`fa-solid fa-house`), and badge for A4 standard.

- [ ] **Step 2: Refine invoice sheet and typography**
Harmonize table borders, badges, words-to-number card (`fa-solid fa-coins`), notes section, and signature boxes. Ensure `@media print` strictly hides web navigation and prints cleanly.

- [ ] **Step 3: Verify test suite passes**
Run: `docker exec work_time_web python manage.py test timesheet`
Expected: 7 tests pass.

- [ ] **Step 4: Commit Task 6**
```bash
git add timesheet/templates/factor.html
git commit -m "feat(ui): modernize invoice page toolbar with FontAwesome and clean print layout"
```

---

### Task 7: Full Integration and Visual Verification

**Files:**
- Test all pages through test suite and curl/HTTP checks
- Check responsiveness and static asset delivery

- [ ] **Step 1: Run complete Django test suite**
Run: `docker exec work_time_web python manage.py test timesheet`
Expected: OK (7 tests passed).

- [ ] **Step 2: Verify HTTP response status and asset links on live container**
Perform curl requests to `http://localhost:8012/` and static endpoints to confirm 200 OK and valid CSS/JS links.

- [ ] **Step 3: Check git status to ensure clean tree with no temporary files**
Run: `git status`
Expected: Clean working tree.

- [ ] **Step 4: Commit Task 7 summary**
```bash
git commit --allow-empty -m "chore(ui): complete UI/UX redesign and visual polish verification"
```
