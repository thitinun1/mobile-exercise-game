import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ต้องติดตั้ง: pip install streamlit plotly pandas

st.set_page_config(
    page_title="เกมออกกำลังกายมือถือ",
    page_icon="💪",
    layout="centered",  # สำหรับมือถือ
    initial_sidebar_state="collapsed"  # ซ่อน sidebar ตอนเริ่ม
)

# CSS สำหรับมือถือโดยเฉพาะ
st.markdown("""
    <style>
    /* ปรับสำหรับมือถือ */
    .stApp {
        max-width: 100%;
        padding: 0px;
    }
    
    /* ปุ่มใหญ่สำหรับมือถือ */
    .big-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px 20px;
        font-size: 28px;
        font-weight: bold;
        border-radius: 20px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: 0.3s;
        border: none;
        width: 100%;
    }
    
    .big-button:active {
        transform: scale(0.95);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* การ์ดท่าออกกำลังกาย */
    .exercise-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    
    /* ตัวนับเวลา */
    .timer {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #667eea;
        margin: 20px 0;
    }
    
    /* คะแนนและสถิติ */
    .stats {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    /* ปุ่มเมนู */
    .menu-button {
        background: #f0f2f6;
        color: #333;
        padding: 20px;
        font-size: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 5px;
        cursor: pointer;
        border: none;
        width: 100%;
    }
    
    .menu-button:active {
        background: #ddd;
    }
    
    /* ซ่อนเมนู streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ปรับขนาดฟอนต์ */
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    </style>
    
    <!-- เพิ่ม Meta viewport สำหรับมือถือ -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

class MobileExerciseGame:
    def __init__(self):
        if 'initialized' not in st.session_state:
            st.session_state.player_name = ""
            st.session_state.level = 1
            st.session_state.exp = 0
            st.session_state.next_level_exp = 100
            st.session_state.score = 0
            st.session_state.combo = 0
            st.session_state.history = []
            st.session_state.current_exercise = None
            st.session_state.game_active = False
            st.session_state.start_time = None
            st.session_state.reps = 0
            st.session_state.page = "home"  # home, exercises, game, stats
            st.session_state.timer_running = False
            st.session_state.achievements = []
            st.session_state.initialized = True

    def load_exercises(self):
        return {
            'ง่าย': [
                {'name': '👋 กระโดดตบ', 'duration': 15, 'calories': 5, 
                 'desc': 'กระโดดแล้วตบมือ', 'color': '#4CAF50'},
                {'name': '🦵 สควอท', 'duration': 15, 'calories': 4,
                 'desc': 'ย่อตัวเหมือนนั่งเก้าอี้', 'color': '#2196F3'},
                {'name': '🤸 แกว่งแขน', 'duration': 15, 'calories': 3,
                 'desc': 'แกว่งแขนเป็นวงกลม', 'color': '#FF9800'},
            ],
            'ปานกลาง': [
                {'name': '🥊 หมัดสลับ', 'duration': 20, 'calories': 8,
                 'desc': 'ชกสลับซ้าย-ขวา', 'color': '#9C27B0'},
                {'name': '🦵 เตะสูง', 'duration': 20, 'calories': 7,
                 'desc': 'เตะสลับขา', 'color': '#E91E63'},
                {'name': '🏃 วิ่งอยู่กับที่', 'duration': 25, 'calories': 6,
                 'desc': 'วิ่งยกเข่าสูง', 'color': '#FF5722'},
            ],
            'ยาก': [
                {'name': '🤸 เบอร์พี', 'duration': 20, 'calories': 12,
                 'desc': 'ย่อ-วิดพื้น-กระโดด', 'color': '#f44336'},
                {'name': '🧗 เมาน์เทนคลิมเบอร์', 'duration': 20, 'calories': 10,
                 'desc': 'วิ่งปีนเขา', 'color': '#795548'},
            ]
        }

    def show_home(self):
        """หน้าแรก"""
        st.markdown("<h1 style='text-align: center;'>💪 เกมออกกำลังกาย</h1>", unsafe_allow_html=True)
        
        # กรอกชื่อถ้ายังไม่มี
        if not st.session_state.player_name:
            name = st.text_input("ใส่ชื่อของคุณ", placeholder="เช่น สมชาย", key="name_input")
            if name:
                st.session_state.player_name = name
                st.rerun()
        else:
            # แสดงข้อมูลผู้เล่น
            st.markdown(f"""
            <div class='stats'>
                <span class='big-font'>👤 {st.session_state.player_name}</span><br>
                เลเวล {st.session_state.level} | ⭐ EXP: {st.session_state.exp}/{st.session_state.next_level_exp}
            </div>
            """, unsafe_allow_html=True)
            
            # Progress
            exp_percent = (st.session_state.exp / st.session_state.next_level_exp) * 100
            st.progress(min(exp_percent/100, 1.0))
            
            # เมนูหลัก (ปุ่มใหญ่)
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎯 เล่นเลย", use_container_width=True):
                    st.session_state.page = "exercises"
                    st.rerun()
                    
            with col2:
                if st.button("📊 สถิติ", use_container_width=True):
                    st.session_state.page = "stats"
                    st.rerun()
            
            # แสดงสถิติอย่างย่อ
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("คะแนน", st.session_state.score)
            with col2:
                st.metric("คอมโบ", st.session_state.combo)
            with col3:
                st.metric("เล่นแล้ว", len(st.session_state.history))
            
            # ความสำเร็จล่าสุด
            if st.session_state.achievements:
                st.markdown("---")
                st.markdown("🏆 **ความสำเร็จล่าสุด**")
                for ach in st.session_state.achievements[-3:]:
                    st.markdown(f"✅ {ach}")

    def show_exercises(self):
        """หน้าเลือกท่า"""
        st.markdown("""
            <div style='display: flex; align-items: center; margin-bottom: 20px;'>
                <h2>🎯 เลือกท่าออกกำลังกาย</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # ปุ่มกลับ
        if st.button("← กลับหน้าหลัก", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        
        exercises = self.load_exercises()
        
        # แสดงท่าตามความยาก
        for difficulty, ex_list in exercises.items():
            st.markdown(f"### {difficulty}")
            for ex in ex_list:
                with st.container():
                    st.markdown(f"""
                    <div class='exercise-card' style='border-left-color: {ex["color"]};'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-size: 24px;'>{ex["name"]}</span>
                        </div>
                        <p>{ex["desc"]}</p>
                        <p>⏱️ {ex["duration"]} วิ | 🔥 {ex["calories"]} แคล</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("เล่นท่าครับ", key=f"play_{ex['name']}", use_container_width=True):
                        st.session_state.current_exercise = ex
                        st.session_state.page = "game"
                        st.session_state.reps = 0
                        st.session_state.start_time = time.time()
                        st.session_state.timer_running = True
                        st.rerun()

    def show_game(self):
        """หน้าเล่นเกม"""
        if not st.session_state.current_exercise:
            st.session_state.page = "exercises"
            st.rerun()
            
        ex = st.session_state.current_exercise
        
        # หัวข้อ
        st.markdown(f"""
            <div style='text-align: center; margin-bottom: 20px;'>
                <h2>{ex['name']}</h2>
                <p>{ex['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Timer
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, ex['duration'] - elapsed)
        
        # แสดงเวลาถอยหลัง
        st.markdown(f"<div class='timer'>{int(remaining)} วินาที</div>", unsafe_allow_html=True)
        
        # Progress bar
        progress = elapsed / ex['duration']
        st.progress(min(progress, 1.0))
        
        # ปุ่มนับครั้ง (ใหญ่ที่สุด)
        st.markdown("### 👆 กดทุกครั้งที่ทำครบ 1 ครั้ง")
        
        # ปุ่มขนาดใหญ่สำหรับมือถือ
        button_html = """
            <button class='big-button' onclick='alert("นับครั้ง!")'>
                ✅ ทำครบ 1 ครั้ง<br>
                <span style='font-size: 16px;'>กดตรงนี้ทุกครั้ง</span>
            </button>
        """
        
        # ใช้ st.button แทน HTML เพื่อให้ทำงานได้
        if st.button("✅ ทำครบ 1 ครั้ง", key="count_rep", use_container_width=True):
            st.session_state.reps += 1
            st.session_state.combo += 1
            
            # สั่น (ใช้ vibration API ถ้ามี)
            st.markdown("""
                <script>
                if (navigator.vibrate) {
                    navigator.vibrate(100);
                }
                </script>
            """, unsafe_allow_html=True)
            
            st.success(f"✅ ครั้งที่ {st.session_state.reps}")
            st.rerun()
        
        # แสดงจำนวนครั้ง
        st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
            <span style='font-size: 72px; font-weight: bold; color: #667eea;'>{st.session_state.reps}</span>
            <span style='font-size: 24px;'> ครั้ง</span>
        </div>
        """, unsafe_allow_html=True)
        
        # สถิติระหว่างเล่น
        col1, col2 = st.columns(2)
        with col1:
            points = st.session_state.reps * 10
            st.metric("คะแนน", points)
        with col2:
            st.metric("คอมโบ", st.session_state.combo)
        
        # จบเกม
        if elapsed >= ex['duration']:
            # คำนวณคะแนน
            final_score = st.session_state.reps * 10 * (1 + st.session_state.combo * 0.1)
            calories = ex['calories'] * (st.session_state.reps / 10)
            
            # เพิ่ม EXP
            exp_gain = int(final_score / 10)
            st.session_state.exp += exp_gain
            st.session_state.score += final_score
            
            # ตรวจสอบอัพเลเวล
            if st.session_state.exp >= st.session_state.next_level_exp:
                st.session_state.level += 1
                st.session_state.exp -= st.session_state.next_level_exp
                st.session_state.next_level_exp = int(st.session_state.next_level_exp * 1.5)
                st.session_state.achievements.append(f"🎉 เลเวล {st.session_state.level}")
            
            # บันทึกประวัติ
            st.session_state.history.append({
                'datetime': datetime.now(),
                'exercise': ex['name'],
                'reps': st.session_state.reps,
                'score': int(final_score),
                'calories': calories
            })
            
            # แสดงสรุป
            st.balloons()
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin: 20px 0;'>
                <h2>🎉 ทำสำเร็จ!</h2>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ครั้ง", st.session_state.reps)
            with col2:
                st.metric("คะแนน", int(final_score))
            with col3:
                st.metric("EXP", exp_gain)
            
            # ปุ่มกลับ
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎯 เล่นอีก", use_container_width=True):
                    st.session_state.page = "exercises"
                    st.session_state.current_exercise = None
                    st.rerun()
            with col2:
                if st.button("🏠 หน้าหลัก", use_container_width=True):
                    st.session_state.page = "home"
                    st.session_state.current_exercise = None
                    st.rerun()
        
        # ปุ่มยกเลิก
        if st.button("❌ ยกเลิก", use_container_width=True):
            st.session_state.page = "exercises"
            st.session_state.current_exercise = None
            st.rerun()

    def show_stats(self):
        """หน้าสถิติ"""
        st.markdown("<h2 style='text-align: center;'>📊 สถิติของฉัน</h2>", unsafe_allow_html=True)
        
        # ปุ่มกลับ
        if st.button("← กลับหน้าหลัก", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        
        # สถิติรวม
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stats'>
                <span style='font-size: 36px;'>{st.session_state.level}</span><br>
                เลเวล
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stats'>
                <span style='font-size: 36px;'>{st.session_state.score}</span><br>
                คะแนน
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("เล่นทั้งหมด", f"{len(st.session_state.history)} ครั้ง")
        with col2:
            total_calories = sum(h.get('calories', 0) for h in st.session_state.history)
            st.metric("เผาผลาญ", f"{total_calories:.0f} แคล")
        
        # กราฟความคืบหน้า
        if st.session_state.history:
            st.markdown("### 📈 ความคืบหน้า")
            df = pd.DataFrame(st.session_state.history)
            
            fig = px.line(df, x='datetime', y='score', 
                         title='คะแนนแต่ละครั้ง',
                         labels={'score': 'คะแนน', 'datetime': 'เวลา'})
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        
        # ความสำเร็จ
        if st.session_state.achievements:
            st.markdown("### 🏆 ความสำเร็จ")
            for ach in st.session_state.achievements:
                st.markdown(f"✅ {ach}")

# Main app
def main():
    game = MobileExerciseGame()
    
    # แสดงหน้าตามสถานะ
    if st.session_state.page == "home":
        game.show_home()
    elif st.session_state.page == "exercises":
        game.show_exercises()
    elif st.session_state.page == "game":
        game.show_game()
    elif st.session_state.page == "stats":
        game.show_stats()

if __name__ == "__main__":
    main()