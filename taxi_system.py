import folium
from geopy.distance import geodesic
from geopy.geocoders import GoogleV3
import webbrowser

# ملاحظة: يجب إنشاء ملف config.py وإضافة مفتاح API الخاص بك فيه
# from config import GOOGLE_MAPS_API_KEY
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"  # استبدلها بمفتاحك الفعلي

class TaxiSystem:
    def __init__(self):
        self.customers = {}
        self.drivers = {}
        self.rides = {}
        self.current_id = 1
        self.price_per_km = 1.5  # سعر الكيلومتر بالدينار الليبي
        
        # قائمة المدن الليبية مع إحداثيات GPS
        self.libyan_cities = {
            "طرابلس": (32.8872, 13.1913),
            "بنغازي": (32.1167, 20.0667),
            "مصراتة": (32.3783, 15.0906),
            "سبها": (27.0333, 14.4333),
            "طبرق": (32.0833, 23.9667),
            "الزاوية": (32.7572, 12.7278),
            "غات": (24.9647, 10.1683),
            "نالوت": (31.8683, 10.9828),
            "درنة": (32.7667, 22.6333),
            "الأبيار": (32.1833, 20.5833),
        }
        
        self.geolocator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)

    # تسجيل عميل جديد
    def register_customer(self, name, phone):
        customer_id = self.current_id
        self.customers[customer_id] = {"name": name, "phone": phone}
        self.current_id += 1
        print(f"✅ تم تسجيل العميل رقم {customer_id}")

    # تسجيل سائق جديد
    def register_driver(self, name, car_number):
        driver_id = self.current_id
        self.drivers[driver_id] = {
            "name": name,
            "car": car_number,
            "available": True
        }
        self.current_id += 1
        print(f"🚕 تم تسجيل السائق رقم {driver_id}")

    # حساب المسافة بين مدينتين
    def calculate_distance(self, start_city, end_city):
        start = self.libyan_cities.get(start_city)
        end = self.libyan_cities.get(end_city)
        if not start or not end:
            return None
        return geodesic(start, end).kilometers

    # إنشاء خريطة تفاعلية
    def generate_map(self, start_city, end_city, ride_id):
        start_coords = self.libyan_cities[start_city]
        end_coords = self.libyan_cities[end_city]
        
        # إنشاء خريطة مركزها ليبيا
        m = folium.Map(location=[26.3351, 17.2283], zoom_start=6)
        
        # إضافة علامات المدن
        folium.Marker(
            start_coords,
            popup=f"بداية الرحلة: {start_city}",
            icon=folium.Icon(color="green", icon="car", prefix="fa")
        ).add_to(m)
        
        folium.Marker(
            end_coords,
            popup=f"نهاية الرحلة: {end_city}",
            icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa")
        ).add_to(m)
        
        # إضافة خط بين المدينتين
        folium.PolyLine(
            [start_coords, end_coords],
            color="blue",
            weight=2.5,
            opacity=0.8
        ).add_to(m)
        
        # حفظ الخريطة في ملف
        filename = f"ride_{ride_id}_map.html"
        m.save(filename)
        return filename

    # طلب رحلة جديدة
    def request_ride(self, customer_id, start_city, end_city):
        if customer_id not in self.customers:
            print("❌ العميل غير مسجل!")
            return

        # البحث عن سائق متاح
        driver_id = None
        for d_id, driver in self.drivers.items():
            if driver["available"]:
                driver_id = d_id
                break

        if not driver_id:
            print("❌ لا يوجد سائقين متاحين الآن!")
            return

        # حساب المسافة والسعر
        distance = self.calculate_distance(start_city, end_city)
        if not distance:
            print("❌ خطأ في تحديد المدن!")
            return

        price = distance * self.price_per_km
        ride_id = self.current_id
        
        # إنشاء الخريطة
        map_file = self.generate_map(start_city, end_city, ride_id)
        
        # حفظ بيانات الرحلة
        self.rides[ride_id] = {
            "customer_id": customer_id,
            "driver_id": driver_id,
            "start": start_city,
            "end": end_city,
            "distance": round(distance, 2),
            "price": round(price, 2),
            "status": "جارية",
            "map": map_file
        }
        
        self.drivers[driver_id]["available"] = False
        self.current_id += 1
        
        print(f"""
        🚖 تم تأكيد الرحلة رقم {ride_id}
        - السائق: {self.drivers[driver_id]['name']}
        - السيارة: {self.drivers[driver_id]['car']}
        - السعر: {round(price, 2)} د.ل
        - الخريطة: {map_file}
        """)

    # عرض تفاصيل الرحلة
    def show_ride_details(self, ride_id):
        ride = self.rides.get(ride_id)
        if not ride:
            print("❌ الرحلة غير موجودة!")
            return
            
        customer = self.customers[ride["customer_id"]]
        driver = self.drivers[ride["driver_id"]]
        
        print(f"""
        📝 تفاصيل الرحلة #{ride_id}
        - العميل: {customer['name']} ({customer['phone']})
        - السائق: {driver['name']} ({driver['car']})
        - المسافة: {ride['distance']} كم
        - السعر: {ride['price']} د.ل
        - الحالة: {ride['status']}
        - الخريطة: {ride['map']}
        """)

# الواجهة الرئيسية
def main():
    system = TaxiSystem()
    while True:
        print("\n" + "="*40)
        print("🚖 نظام إدارة التاكسي الليبي - الإصدار 1.0")
        print("="*40)
        print("1. تسجيل عميل جديد")
        print("2. تسجيل سائق جديد")
        print("3. طلب رحلة")
        print("4. عرض تفاصيل الرحلة")
        print("5. فتح الخريطة")
        print("6. خروج")
        
        choice = input("اختر الخيار: ")
        
        if choice == "1":
            name = input("اسم العميل: ")
            phone = input("رقم الهاتف: ")
            system.register_customer(name, phone)
            
        elif choice == "2":
            name = input("اسم السائق: ")
            car = input("رقم السيارة: ")
            system.register_driver(name, car)
            
        elif choice == "3":
            customer_id = int(input("رقم العميل: "))
            print("المدن المتاحة:", ", ".join(system.libyan_cities.keys()))
            start = input("مدينة الانطلاق: ")
            end = input("مدينة الوصول: ")
            system.request_ride(customer_id, start, end)
            
        elif choice == "4":
            ride_id = int(input("رقم الرحلة: "))
            system.show_ride_details(ride_id)
            
        elif choice == "5":
            ride_id = int(input("رقم الرحلة: "))
            ride = system.rides.get(ride_id)
            if ride:
                webbrowser.open(ride["map"])
            else:
                print("❌ الرحلة غير موجودة!")
                
        elif choice == "6":
            print("شكرًا لاستخدامك النظام!")
            break
            
        else:
            print("❌ خيار غير صحيح!")

if __name__ == "__main__":
    main()
