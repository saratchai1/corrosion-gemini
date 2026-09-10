import re

with open('scripts/build_app_js.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace droneBounds for Phang Nga with composite bounding box
old_drone_bounds = """      droneBounds: [
        [8.349952303062057, 98.55018184554493],
        [8.353712508600562, 98.55320496491346]
      ],"""

new_drone_bounds = """      droneBounds: [
        [8.3443621884707, 98.5494316079051],
        [8.353712508600562, 98.55320496491346]
      ],
      droneBounds40_1: [
        [8.349952303062057, 98.55018184554493],
        [8.353712508600562, 98.55320496491346]
      ],
      droneBounds40_2: [
        [8.3443621884707, 98.5494316079051],
        [8.349004416111159, 98.55291785728623]
      ],"""

content = content.replace(old_drone_bounds, new_drone_bounds)

# Update resolveLayer for Phang Nga
old_resolve = """    if (key === 'drone-phangnga') {
      return {
        url: 'public/data/phangnga/drone/40-vsd_small1_hd.webp',
        bounds: currentProvince.droneBounds,
        badge: '🛸 ภาพโดรน UAV ล่าสุด (40-VSD)'
      };
    }"""

new_resolve = """    if (key === 'drone-phangnga' || key === 'drone-phangnga-40-1') {
      return {
        url: 'public/data/phangnga/drone/40-vsd_small1_hd.webp',
        bounds: currentProvince.droneBounds40_1 || currentProvince.droneBounds,
        badge: '🛸 โดรนแปลง 40-VSD เหนือ (เกาะไม้ไผ่)'
      };
    }
    if (key === 'drone-phangnga-40-2') {
      return {
        url: 'public/data/phangnga/drone/40-vsd_small2_hd.webp',
        bounds: currentProvince.droneBounds40_2 || currentProvince.droneBounds,
        badge: '🛸 โดรนแปลง 40-VSD ใต้ (เกาะไม้ไผ่)'
      };
    }
    if (key === 'drone-phangnga-41') {
      return {
        url: 'public/data/phangnga/drone/41-vsd_hd.webp',
        bounds: currentProvince.droneBounds41 || currentProvince.droneBounds,
        badge: '🛸 โดรนแปลง 41-VSD (เกาะปันหยี)'
      };
    }"""

content = content.replace(old_resolve, new_resolve)

# Update right dates dropdown in temporalDates for Phang Nga
old_right_dates = """        right: [
          { value: 'drone-phangnga', label: '🛸 ภาพโดรน UAV ล่าสุด (40-VSD)' },
          { value: '2026-03-21', label: 'ดาวเทียม มี.ค. 2569 (3 ปี - ปัจจุบัน)' },
          { value: '2024-03-19', label: 'ดาวเทียม มี.ค. 2567 (1 ปีหลังปลูก)' }
        ],"""

new_right_dates = """        right: [
          { value: 'drone-phangnga-40-1', label: '🛸 โดรนแปลง 40-VSD เหนือ (เกาะไม้ไผ่)' },
          { value: 'drone-phangnga-40-2', label: '🛸 โดรนแปลง 40-VSD ใต้ (เกาะไม้ไผ่)' },
          { value: 'drone-phangnga-41', label: '🛸 โดรนแปลง 41-VSD (เกาะปันหยี)' },
          { value: '2026-03-21', label: 'ดาวเทียม มี.ค. 2569 (3 ปี - ปัจจุบัน)' },
          { value: '2024-03-19', label: 'ดาวเทียม มี.ค. 2567 (1 ปีหลังปลูก)' }
        ],"""

content = content.replace(old_right_dates, new_right_dates)

# Update resolution dates for Phang Nga
old_res_dates = """      resolutionDates: [
        { value: 'drone-phangnga', label: '🛸 ภาพโดรน UAV ล่าสุด (40-VSD)' },
        { value: '2026-03-21', label: 'ปี 2569 (3 ปีหลังปลูก - ปัจจุบัน)' },
        { value: '2024-03-19', label: 'ปี 2567 (1 ปีหลังปลูก)' },
        { value: '2023-04-11', label: 'ปี 2566 (ก่อนเริ่มปลูก - Baseline)' }
      ],"""

new_res_dates = """      resolutionDates: [
        { value: 'drone-phangnga-40-1', label: '🛸 โดรนแปลง 40-VSD เหนือ (เกาะไม้ไผ่)' },
        { value: 'drone-phangnga-40-2', label: '🛸 โดรนแปลง 40-VSD ใต้ (เกาะไม้ไผ่)' },
        { value: 'drone-phangnga-41', label: '🛸 โดรนแปลง 41-VSD (เกาะปันหยี)' },
        { value: '2026-03-21', label: 'ปี 2569 (3 ปีหลังปลูก - ปัจจุบัน)' },
        { value: '2024-03-19', label: 'ปี 2567 (1 ปีหลังปลูก)' },
        { value: '2023-04-11', label: 'ปี 2566 (ก่อนเริ่มปลูก - Baseline)' }
      ],"""

content = content.replace(old_res_dates, new_res_dates)

with open('scripts/build_app_js.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated scripts/build_app_js.py successfully!")
