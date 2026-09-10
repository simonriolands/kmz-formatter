import streamlit as st
import zipfile
import os
import shutil
import xml.etree.ElementTree as ET
import copy
import tempfile
import re

def hex_to_kml_color(hex_color):
    if not hex_color or str(hex_color).strip() == "":
        return "" 
    hex_color = hex_color.replace("#", "")
    if len(hex_color) == 6:
        r = hex_color[0:2]
        g = hex_color[2:4]
        b = hex_color[4:6]
        return f"ff{b}{g}{r}".lower()
    return hex_color

def proses_kmz(input_path, output_path, extract_dir):
    # Definisi properti dasar untuk Shared Style
    style_rules_titik = {
        "FAT": {"warna": "#FFFF00", "warna_teks": "#FFFF00", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/triangle.png"},
        "HP COVER": {"warna": "#00FF00", "warna_teks": "#00FF00", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png"},
        "HP UNCOVER": {"warna": "#FF0000", "warna_teks": "#FF0000", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/homegardenbusiness.png"},
        "EXISTING POLE EMR 7-2.5": {"warna": "#FFFFFF", "warna_teks": "#FFFFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "EXISTING POLE EMR 7-3": {"warna": "#FFFFFF", "warna_teks": "#FFFFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "EXISTING POLE EMR 7-4": {"warna": "#FFFFFF", "warna_teks": "#FFFFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "EXISTING POLE EMR 9-4": {"warna": "#FFFFFF", "warna_teks": "#FFFFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "EXISTING POLE PARTNER 7-4": {"warna": "#FFFFFF", "warna_teks": "#FFFFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "EXISTING POLE PARTNER 9-4": {"warna": "#FFFFFF", "warna_teks": "#FFFFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "NEW POLE 7-2.5": {"warna": "#AA00FF", "warna_teks": "#AA00FF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "NEW POLE 7-3": {"warna": "#00FFFF", "warna_teks": "#00FFFF", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "NEW POLE 7-4": {"warna": "#00FF00", "warna_teks": "#00FF00", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "NEW POLE 9-4": {"warna": "#FF0000", "warna_teks": "#FF0000", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"},
        "SLACK HANGER": {"warna": "#FF0000", "warna_teks": "#FF0000", "ukuran": "0.8", "ukuran_teks": "0.8", "icon": "http://maps.google.com/mapfiles/kml/shapes/target.png"}
    }

    style_rules_garis = {
        "DISTRIBUTION CABLE": {"warna": "", "ketebalan": "3"},
        "SLING WIRE": {"warna": "#00FFFF", "ketebalan": "3"}
    }

    folder_existing_pole = [
        "EXISTING POLE EMR 7-2.5", "EXISTING POLE EMR 7-3", "EXISTING POLE EMR 7-4", "EXISTING POLE EMR 9-4", 
        "EXISTING POLE PARTNER 7-4", "EXISTING POLE PARTNER 9-4"
    ]

    daftar_folder_standar = [
        "BOUNDARY FAT", "FAT", "HP COVER", "HP UNCOVER", "EXISTING POLE EMR 7-2.5", "EXISTING POLE EMR 7-3", 
        "EXISTING POLE EMR 7-4", "EXISTING POLE EMR 9-4", "EXISTING POLE PARTNER 7-4", "EXISTING POLE PARTNER 9-4", 
        "NEW POLE 7-2.5", "NEW POLE 7-3", "NEW POLE 7-4", "NEW POLE 9-4", "DISTRIBUTION CABLE", "SLACK HANGER", "SLING WIRE"
    ]

    with zipfile.ZipFile(input_path, 'r') as kmz:
        kmz.extractall(extract_dir)

    file_kml = None
    for file in os.listdir(extract_dir):
        if file.endswith(".kml"):
            file_kml = os.path.join(extract_dir, file)
            break

    if not file_kml:
        raise Exception("File KML tidak ditemukan di dalam KMZ.")

    with open(file_kml, 'r', encoding='utf-8') as f:
        kml_data = f.read()

    namespaces_wajib = [
        ('xmlns:gx', '"http://www.google.com/kml/ext/2.2"'),
        ('xmlns:kml', '"http://www.opengis.net/kml/2.2"'),
        ('xmlns:atom', '"http://www.w3.org/2005/Atom"'),
        ('xmlns:xal', '"urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"'),
        ('xmlns:xsi', '"http://www.w3.org/2001/XMLSchema-instance"')
    ]

    kml_tag_match = re.search(r'<kml[^>]*>', kml_data)
    if kml_tag_match:
        kml_tag = kml_tag_match.group(0)
        new_kml_tag = kml_tag
        if '<kml>' in new_kml_tag:
            new_kml_tag = new_kml_tag.replace('<kml>', '<kml >')
        
        for ns, url in namespaces_wajib:
            if ns not in new_kml_tag:
                new_kml_tag = new_kml_tag.replace('<kml ', f'<kml {ns}={url} ')
        
        if new_kml_tag != kml_tag:
            kml_data = kml_data.replace(kml_tag, new_kml_tag)
            with open(file_kml, 'w', encoding='utf-8') as f:
                f.write(kml_data)

    namespace_kml = "http://www.opengis.net/kml/2.2"
    namespace_gx = "http://www.google.com/kml/ext/2.2"
    ET.register_namespace('', namespace_kml)
    ET.register_namespace('gx', namespace_gx)
    ET.register_namespace('atom', "http://www.w3.org/2005/Atom")
    ns = {'kml': namespace_kml, 'gx': namespace_gx}
    
    tree = ET.parse(file_kml)
    root = tree.getroot()

    # Cari atau buat tag <Document> di root untuk menaruh Shared Style
    document_elem = root.find('kml:Document', ns)
    if document_elem is None:
        document_elem = root.find('Document')
    if document_elem is None:
        document_elem = ET.SubElement(root, '{%s}Document' % namespace_kml)

    # ==========================================
    # BUAT SHARED STYLES DI LEVEL DOCUMENT
    # ==========================================
    def buat_shared_style(style_id, warna_titik, warna_teks, ukuran, icon_url, hide_balloon=True):
        style_elem = ET.SubElement(document_elem, '{%s}Style' % namespace_kml, attrib={f'{{{namespace_kml}}}id': style_id})
        
        if hide_balloon:
            b_style = ET.SubElement(style_elem, '{%s}BalloonStyle' % namespace_kml)
            ET.SubElement(b_style, '{%s}displayMode' % namespace_kml).text = "hide"
            
        icon_style = ET.SubElement(style_elem, '{%s}IconStyle' % namespace_kml)
        if warna_titik:
            ET.SubElement(icon_style, '{%s}color' % namespace_kml).text = hex_to_kml_color(warna_titik)
        ET.SubElement(icon_style, '{%s}scale' % namespace_kml).text = ukuran
        icon = ET.SubElement(icon_style, '{%s}Icon' % namespace_kml)
        ET.SubElement(icon, '{%s}href' % namespace_kml).text = icon_url
        
        label_style = ET.SubElement(style_elem, '{%s}LabelStyle' % namespace_kml)
        if warna_teks:
            ET.SubElement(label_style, '{%s}color' % namespace_kml).text = hex_to_kml_color(warna_teks)
        ET.SubElement(label_style, '{%s}scale' % namespace_kml).text = ukuran

    def buat_shared_line_style(style_id, warna_garis, ketebalan, hide_balloon=True):
        style_elem = ET.SubElement(document_elem, '{%s}Style' % namespace_kml, attrib={f'{{{namespace_kml}}}id': style_id})
        
        if hide_balloon:
            b_style = ET.SubElement(style_elem, '{%s}BalloonStyle' % namespace_kml)
            ET.SubElement(b_style, '{%s}displayMode' % namespace_kml).text = "hide"
            
        line_style = ET.SubElement(style_elem, '{%s}LineStyle' % namespace_kml)
        if warna_garis:
            ET.SubElement(line_style, '{%s}color' % namespace_kml).text = hex_to_kml_color(warna_garis)
        ET.SubElement(line_style, '{%s}width' % namespace_kml).text = ketebalan

    # Daftarkan shared styles untuk titik standar
    for kat, aturan in style_rules_titik.items():
        style_id_name = f"shared_style_{kat.replace(' ', '_')}"
        buat_shared_style(style_id_name, aturan['warna'], aturan['warna_teks'], aturan['ukuran'], aturan['icon'], hide_balloon=True)

    # Daftarkan shared styles khusus FDT (berdasarkan core)
    fdt_core_colors = [("#FF0000", "fdt_96c"), ("#550000", "fdt_72c"), ("#AA00FF", "fdt_48c"), ("#FFFFFF", "fdt_sharing")]
    for warna_fdt, fdt_key in fdt_core_colors:
        buat_shared_style(f"shared_style_{fdt_key}", warna_fdt, warna_fdt, "0.8", "http://maps.google.com/mapfiles/kml/shapes/cross-hairs.png", hide_balloon=True)

    # Style untuk Slack Hanger tiruan FDT
    buat_shared_style("shared_style_slack_hanger_copy", "#FFFFFF", "#FFFFFF", "0.8", "http://maps.google.com/mapfiles/kml/shapes/target.png", hide_balloon=True)

    # Style untuk Kabel / Garis
    buat_shared_style_line_24c = "shared_style_cable_24c"
    buat_shared_style_line_36c = "shared_style_cable_36c"
    buat_shared_style_line_48c = "shared_style_cable_48c"
    buat_shared_style_sling = "shared_style_sling_wire"
    buat_shared_style_dist = "shared_style_dist_cable"

    buat_shared_line_style(buat_shared_style_line_24c, "#00FF00", "3", hide_balloon=True)
    buat_shared_line_style(buat_shared_style_line_36c, "#FF00FF", "3", hide_balloon=True)
    buat_shared_line_style(buat_shared_style_line_48c, "#AA00FF", "3", hide_balloon=True)
    buat_shared_line_style(buat_shared_style_sling, "#00FFFF", "3", hide_balloon=True)
    buat_shared_line_style(buat_shared_style_dist, "", "3", hide_balloon=True)

    parent_map = {c: p for p in root.iter() for c in p}

    def get_kategori(folder_elem):
        curr = folder_elem
        while curr is not None:
            if curr.tag == f'{{{namespace_kml}}}Folder' or curr.tag == 'Folder':
                nama_elem = curr.find('kml:name', ns)
                if nama_elem is None: nama_elem = curr.find('name')
                if nama_elem is not None and nama_elem.text:
                    nama = nama_elem.text.strip().upper()
                    if (nama in style_rules_titik or 
                        nama in style_rules_garis or 
                        nama == "FDT" or 
                        "CABLE" in nama or 
                        "BOUNDARY" in nama):
                        return nama
            curr = parent_map.get(curr)
        
        nama_elem = folder_elem.find('kml:name', ns)
        if nama_elem is None: nama_elem = folder_elem.find('name')
        return nama_elem.text.strip().upper() if (nama_elem is not None and nama_elem.text) else ""

    # Bersihkan style di level folder agar tidak konflik
    for folder_elem in root.findall('.//kml:Folder', ns) + root.findall('.//Folder'):
        for f_style in list(folder_elem.findall('kml:Style', ns) + folder_elem.findall('Style') + folder_elem.findall('kml:StyleMap', ns) + folder_elem.findall('StyleMap')):
            folder_elem.remove(f_style)

    # Bersihkan global placemark tags
    for placemark in root.findall('.//kml:Placemark', ns) + root.findall('.//Placemark'):
        for hapus_tag in ['TimeStamp', 'TimeSpan', 'ExtendedData', 'kml:TimeStamp', 'kml:TimeSpan', 'kml:ExtendedData']:
            tag_elem = placemark.find(hapus_tag, ns)
            if tag_elem is not None:
                placemark.remove(tag_elem)

    # Pra-pemrosesan folder line
    for folder in root.findall('.//kml:Folder', ns) + root.findall('.//Folder'):
        nama_folder_elem = folder.find('kml:name', ns)
        if nama_folder_elem is None: nama_folder_elem = folder.find('name')
        if nama_folder_elem is not None and nama_folder_elem.text:
            nama_folder = nama_folder_elem.text.strip().upper()
            if nama_folder.startswith("LINE"):
                semua_elemen_anak = list(folder)
                sub_folders_dict = {}
                elemen_lainnya = []
                
                for anak in semua_elemen_anak:
                    if anak.tag.endswith('Folder'):
                        sub_nama_elem = anak.find('kml:name', ns)
                        if sub_nama_elem is None: sub_nama_elem = anak.find('name')
                        sub_nama = sub_nama_elem.text.strip().upper() if (sub_nama_elem is not None and sub_nama_elem.text) else ""
                        sub_folders_dict[sub_nama] = anak
                    else:
                        elemen_lainnya.append(anak)
                
                for nama_target in daftar_folder_standar:
                    if nama_target not in sub_folders_dict:
                        folder_baru = ET.Element(f'{{{namespace_kml}}}Folder')
                        nama_elemen_baru = ET.SubElement(folder_baru, f'{{{namespace_kml}}}name')
                        nama_elemen_baru.text = nama_target
                        sub_folders_dict[nama_target] = folder_baru
                
                for anak in semua_elemen_anak:
                    folder.remove(anak)
                for elemen in elemen_lainnya:
                    folder.append(elemen)
                for nama_target in daftar_folder_standar:
                    if nama_target in sub_folders_dict:
                        folder.append(sub_folders_dict[nama_target])
                        del sub_folders_dict[nama_target]
                for sisa_nama, sisa_folder in sub_folders_dict.items():
                    folder.append(sisa_folder)

    # Proses Utama Menggunakan Shared StyleUrl
    for folder in root.findall('.//kml:Folder', ns) + root.findall('.//Folder'):
        kategori_efektif = get_kategori(folder)
        if not kategori_efektif:
            continue

        is_kecuali = ("FDT" in kategori_efektif) or ("CABLE" in kategori_efektif) or ("BOUNDARY" in kategori_efektif)
        
        for placemark in folder.findall('./kml:Placemark', ns) + folder.findall('./Placemark'):
            if not is_kecuali:
                for tag in ['kml:description', 'kml:Snippet', 'gx:balloonVisibility', 'description', 'Snippet', 'balloonVisibility']:
                    elem_to_remove = placemark.find(tag, ns)
                    if elem_to_remove is not None:
                        placemark.remove(elem_to_remove)

            # Hapus style lama/inline style milik placemark
            for tag_to_remove in ['kml:styleUrl', 'kml:Style', 'kml:StyleMap', 'styleUrl', 'Style', 'StyleMap']:
                for elem_to_remove in list(placemark.findall(tag_to_remove, ns) + placemark.findall(tag_to_remove)):
                    placemark.remove(elem_to_remove)

            # --- APLIKASI STYLEURL BERDASARKAN KATEGORI ---
            if kategori_efektif in style_rules_titik:
                if kategori_efektif in folder_existing_pole:
                    nama_placemark_elem = placemark.find('kml:name', ns)
                    if nama_placemark_elem is None: nama_placemark_elem = placemark.find('name')
                    if nama_placemark_elem is not None and nama_placemark_elem.text:
                        nama_asli = nama_placemark_elem.text.strip()
                        if "EXT." not in nama_asli.upper():
                            nama_placemark_elem.text = "EXT." + nama_asli

                style_id_ref = f"#shared_style_{kategori_efektif.replace(' ', '_')}"
                style_url_elem = ET.SubElement(placemark, '{%s}styleUrl' % namespace_kml)
                style_url_elem.text = style_id_ref

            elif kategori_efektif in style_rules_garis:
                nama_placemark_elem = placemark.find('kml:name', ns)
                if nama_placemark_elem is None: nama_placemark_elem = placemark.find('name')
                nama_placemark = nama_placemark_elem.text.strip().upper() if nama_placemark_elem is not None and nama_placemark_elem.text else ""
                
                style_id_ref = "#shared_style_dist_cable"
                if kategori_efektif == "SLING WIRE":
                    style_id_ref = "#shared_style_sling_wire"
                elif kategori_efektif == "DISTRIBUTION CABLE":
                    if "24C/2T" in nama_placemark: style_id_ref = "#shared_style_cable_24c"
                    elif "36C/3T" in nama_placemark: style_id_ref = "#shared_style_cable_36c"
                    elif "48C/4T" in nama_placemark: style_id_ref = "#shared_style_cable_48c"

                style_url_elem = ET.SubElement(placemark, '{%s}styleUrl' % namespace_kml)
                style_url_elem.text = style_id_ref
        
            elif kategori_efektif == "FDT":
                desc_elem = placemark.find('kml:description', ns)
                if desc_elem is None: desc_elem = placemark.find('description')
                desc_text = desc_elem.text.strip().upper() if desc_elem is not None and desc_elem.text else ""
                
                fdt_style_ref = None
                if "96C" in desc_text: fdt_style_ref = "#shared_style_fdt_96c"
                elif "72C" in desc_text: fdt_style_ref = "#shared_style_fdt_72c"
                elif "48C" in desc_text: fdt_style_ref = "#shared_style_fdt_48c"
                elif "SHARING" in desc_text: fdt_style_ref = "#shared_style_fdt_sharing"
                    
                if fdt_style_ref is not None:
                    style_url_elem = ET.SubElement(placemark, '{%s}styleUrl' % namespace_kml)
                    style_url_elem.text = fdt_style_ref

    # ==========================================
    # LOGIKA C: Copy FDT ke Slack Hanger
    # ==========================================
    list_placemark_template = []
    for folder in root.findall('.//kml:Folder', ns) + root.findall('.//Folder'):
        kategori_efektif = get_kategori(folder)
        if kategori_efektif == "FDT":
            for titik_asli in folder.findall('./kml:Placemark', ns) + folder.findall('./Placemark'): 
                placemark_copy = copy.deepcopy(titik_asli) 

                for hapus_tag in ['kml:description', 'kml:Snippet', 'gx:balloonVisibility', 'description', 'Snippet', 'balloonVisibility']:
                    tag_elem = placemark_copy.find(hapus_tag, ns)
                    if tag_elem is not None:
                        placemark_copy.remove(tag_elem)
                        
                for tag_to_remove in ['kml:styleUrl', 'kml:Style', 'kml:StyleMap', 'styleUrl', 'Style', 'StyleMap']:
                    for elem_to_remove in list(placemark_copy.findall(tag_to_remove, ns) + placemark_copy.findall(tag_to_remove)):
                        placemark_copy.remove(elem_to_remove)

                nama_elem = placemark_copy.find('kml:name', ns)
                if nama_elem is None: nama_elem = placemark_copy.find('name')
                if nama_elem is None: nama_elem = ET.SubElement(placemark_copy, '{%s}name' % namespace_kml)
                nama_elem.text = "EXT.SLACK.FDT"

                style_url_elem = ET.SubElement(placemark_copy, '{%s}styleUrl' % namespace_kml)
                style_url_elem.text = "#shared_style_slack_hanger_copy"
                
                list_placemark_template.append(placemark_copy)

    if list_placemark_template:
        berhasil_paste = False
        for folder_induk in root.findall('.//kml:Folder', ns) + root.findall('.//Folder'):
            nama_induk = folder_induk.find('kml:name', ns)
            if nama_induk is None: nama_induk = folder_induk.find('name')
            if nama_induk is not None and nama_induk.text and nama_induk.text.strip().upper().startswith("LINE"):
                for folder_anak in folder_induk.findall('./kml:Folder', ns) + folder_induk.findall('./Folder'):
                    nama_anak = folder_anak.find('kml:name', ns)
                    if nama_anak is None: nama_anak = folder_anak.find('name')
                    if nama_anak is not None and nama_anak.text and nama_anak.text.strip().upper() == "SLACK HANGER":
                        for p_template in list_placemark_template:
                            folder_anak.append(copy.deepcopy(p_template))
                        berhasil_paste = True
                        break
            if berhasil_paste: break

    tree.write(file_kml, encoding='utf-8', xml_declaration=True)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as new_kmz:
        for root_dir, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(file_path, extract_dir)
                new_kmz.write(file_path, arcname)

st.set_page_config(page_title="KMZ Auto-Formatter", page_icon="🌍")

st.title("🌍 KMZ Auto-Formatter & Cleaner")
st.write("Skrip mutakhir: Menggunakan metode Shared Style (styleUrl) standar KML untuk menghilangkan peringatan Google Earth dan menstandarisasi skala 0.8 secara mutlak.")

uploaded_file = st.file_uploader("Pilih file KMZ", type=["kmz"])

if uploaded_file is not None:
    st.info("File berhasil diunggah!")
    
    if st.button("🚀 Proses dan Standarisasi KMZ"):
        with st.spinner('Memproses file spasial...'):
            try:
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, "input.kmz")
                output_path = os.path.join(temp_dir, "output.kmz")
                extract_dir = os.path.join(temp_dir, "extracted")
                
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                proses_kmz(input_path, output_path, extract_dir)
                
                with open(output_path, "rb") as f:
                    hasil_bytes = f.read()
                
                st.success("Berhasil! File KMZ Anda sudah bersih menggunakan metode Shared Style.")
                
                st.download_button(
                    label="⬇️ Download File KMZ Hasil",
                    data=hasil_bytes,
                    file_name=f"STANDAR_{uploaded_file.name}",
                    mime="application/vnd.google-earth.kmz"
                )
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
            finally:
                if 'temp_dir' in locals():
                    shutil.rmtree(temp_dir)
