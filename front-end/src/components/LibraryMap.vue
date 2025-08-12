<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import L from "leaflet";
 import "leaflet/dist/leaflet.css";
 import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
 import markerIcon from 'leaflet/dist/images/marker-icon.png';
 import markerShadow from 'leaflet/dist/images/marker-shadow.png';
 import "leaflet.markercluster/dist/leaflet.markercluster.js";
 import "leaflet.markercluster/dist/MarkerCluster.css";
 import "leaflet.markercluster/dist/MarkerCluster.Default.css";
 import LibraryLink from './LibraryLink.vue';
 import EntryBox from './EntryBox.vue';
 import SearchBar from '../components/SearchBar.vue'
 delete L.Icon.Default.prototype._getIconUrl;
 L.Icon.Default.mergeOptions({
     iconRetinaUrl: markerIcon2x,
     iconUrl: markerIcon,
     shadowUrl: markerShadow,
 });
 export default {
     components: {
         LibraryLink,
         EntryBox,
         SearchBar,
     },
     data() {
         return {
             query: '',
             map: null,
             marker_cluster_group: null,
             msg: null,
             imgWidth: 1200,
             imgHeight: 1200,
             is_initialized: false,
             all_libraries: [],
             libraries: [],
             latest_entries: [],
             all_libraries_count: 0,
             areas: [
                 {
                     // $gettext("Europe")
                     title: "Europe",
                     coords: "400,271 320,395 370,410 425,415 495,400 510,375 500,325 460,290",
                     center: [46.0037, 8.9511],
                     fill: "deepskyblue", stroke: "blue"
                 },
                 {
                     // $gettext("Asia")
                     title: "Asia",
                     coords: "411,0 411,197 400,271 460,290 500,325 510,375 495,400 520,440 575,440 650,475 675,415 790,475 925,425 980,470 930,515 915,700 1030,865 1200,880 1200,0",
                     center: [39.9042, 116.4074],
                     fill: "yellow", stroke: "goldenrod"
                 },
                 {
                     // $gettext("Africa")
                     title: "Africa",
                     center: [-4.4419, 15.2663],
                     coords: "370,410 425,415 495,400 520,440 575,440 575,580 470,650 345,490",
                     fill: "orange", stroke: "orangered"
                 },
                 {
                     // $gettext("Oceania")
                     title: "Oceania",
                     coords: "650,475 675,415 790,475 925,425 980,470 930,515 915,700 735,785 660,625",
                     center: [-33.8688, 151.2093],
                     fill: "green", stroke: "darkgreen"
                 },
                 {
                     // $gettext("North America East")
                     title: "North America East",
                     coords: "0,0 411,0 411,197 400,271 320,395 155,395 70,380 0,371",
                     center: [ 40.7128, -74.0060 ],
                     fill: "purple", stroke: "indigo"
                 },
                 {
                     // $gettext("Center America East")
                     title: "Center America East",
                     coords: "320,395 155,395 70,380 0,371 0,585 152,480 228,480",
                     center: [ 20.6597, -103.3496 ],
                     fill: "pink", stroke: "mediumvioletred"
                 },
                 {
                     // $gettext("North America West")
                     title: "North America West",
                     coords: "960,1200 815,1000 1030,865 1200,880 1200,1200",
                     center: [ 34.0522, -118.2437 ],
                     fill: "lightblue", stroke: "blue"
                 },
                 {
                     // $gettext("Center America West")
                     title: "Center America West",
                     coords: "665,1040 725,1200 960,1200 815,1000",
                     center: [ 21.5218, -77.7812 ],
                     fill: "brown", stroke: "chocolate"
                 },
                 {
                     // $gettext("South America")
                     title: "South America",
                     coords: "0,585 152,480 228,480 375,575 520,770 665,1040 725,1200 0,1200",
                     center: [ -34.0637, -58.3816 ],
                     fill: "red", stroke: "darkred"
                 }
             ],
         }
     },
     methods: {
         async fetch_markers() {
             const res = await axios.get('/collector/api/libraries');
             const markers = res.data.libraries.filter((l) => l.latitude && l.longitude)
             console.log(markers);
             this.marker_cluster_group.clearLayers();
             markers.forEach(m => {
                 const div = document.createElement("div")
                 const link = document.createElement("a");
                 link.href = `/library/details/${m.id}`;
                 link.target = "_blank";
                 if (m.logo_url) {
                     const img = document.createElement("img");
                     img.classList.add("library-logo-in-map");
                     img.src = m.logo_url;
                     link.appendChild(img);
                 }
                 const inner_div = document.createElement("div");
                 inner_div.classList.add("library-link-in-map");
                 inner_div.textContent = m.name;
                 link.appendChild(inner_div);
                 div.appendChild(link);
                 L.marker([m.latitude, m.longitude])
                  .addTo(this.marker_cluster_group)
                  .bindPopup(div);
                 this.libraries.push(m);
                 this.all_libraries.push(m);
             });
             this.update_visible_markers();
         },
         handle_area_click(area) {
             if (!this.is_initialized) {
                 this.initialize_big_map();
             }
             this.map.setView(area.center, 4);
         },
         initialize_big_map() {
             this.$refs.mapContainer.style.height = `${this.$refs.mapContainer.offsetWidth}px`;
             this.is_initialized = true;
             this.map = L.map(this.$refs.mapContainer, { minZoom: 1 });
             this.map.setView(this.areas[0].center, 4);
             L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                 attribution:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
             }).addTo(this.map);
             this.marker_cluster_group = L.markerClusterGroup();
             this.marker_cluster_group.addTo(this.map);
             this.fetch_markers();
             this.map.on('moveend', e => this.update_visible_markers());
             this.map.on('zoomend', e => this.update_visible_markers());
             // this.$refs.mapContainer.scrollIntoView({ behavior: "smooth" });
         },
         update_visible_markers() {
             console.log("Called update visible markers");
             const map_bounds = this.map.getBounds();
             console.log(map_bounds);
             this.libraries = this.all_libraries.filter((l) => {
                 if (map_bounds.contains(L.latLng(l.latitude, l.longitude))) {
                     return true;
                 }
                 else {
                     return false;
                 }
             });
         },
         get_latest_entries() {
             let params = new URLSearchParams;
             if (this.query) {
                 params.append('query', this.query);
             }
             axios.get('/collector/api/latest',
                       { params: params })
                  .then((res) => {
                      console.log("Fetched");
                      this.latest_entries = res.data.entries;
                  });
         }
     },
     mounted() {
         this.get_latest_entries();
         axios.get('/collector/api/libraries')
              .then(res => {
                  this.all_libraries_count = res.data.libraries.length;
              });
     },
     watch: {
         query() {
             this.get_latest_entries();
         }
     },
 }
</script>
<style>
 .leaflet-control-attribution .leaflet-attribution-flag {
     display: none !important;
 }
 img.library-logo-in-map {
     max-width: 150px;
     margin: 2px auto 10px auto;
 }
 .library-link-in-map {
     text-align: center;
 }

</style>
<template>
  <SearchBar class="m-1" v-model="query" />
  <div class="mt-4 m-1 sm:grid sm:grid-cols-2 sm:gap-8 xl:grid-cols-[600px_auto]">
    <div class="sm:mt-12">
      <div v-if="!is_initialized">
        <svg
            class="border-4 rounded-sm"
            :viewBox="`0 0 ${imgWidth} ${imgHeight}`"
            style="width: 100%; height: auto; display: block;"
            xmlns="http://www.w3.org/2000/svg">
          <!-- Actual image -->
          <image href="/spilhaus.jpg" x="0" y="0" :width="imgWidth" :height="imgHeight" />
          <!-- Polygons for each continent/area -->
          <polygon
              v-for="area in areas"
              :key="area.title"
              :points="area.coords"
              :fill="area.fill"
              :stroke="area.stroke"
              :stroke-width="0"
              fill-opacity="0"
              style="cursor:pointer;"
              @click="handle_area_click(area)"
          >
            <title>{{ $gettext(area.title) }}</title>
          </polygon>
        </svg>
        <div @click="handle_area_click(areas[0])" class="mt-2 mcrz-href-primary text-center">
          {{ $gettext('Click on the map to locate a physical library') }}
        </div>
      </div>
      <div ref="mapContainer" class="m-1"></div>
      <div v-for="library in libraries" class="mx-1 my-2 mcrz-plain-box py-1 px-2">
        <router-link :to="{ name: 'library_view', params: { id: library.id } }">
          <span :class="`mcrz-library-${library.library_type || 'digital'}`">
            {{ library.name }}
          </span>
        </router-link>
        <span class="px-1">{{ library.address_city }}</span>
        <span v-if="library.address_country" class="px-1">({{ library.address_country }})</span>
      </div>
      <div class="mt-4 mb-8" v-if="all_libraries_count">
        <div class="mx-auto text-center btn-accent p-2 mx-2 rounded-sm">
          <router-link :to="{ name: 'library_overview' }">
            {{ $gettext('See all the physical and digital libraries (%1)', all_libraries_count) }}
          </router-link>
        </div>
      </div>
    </div>
    <div>
      <h2 class="mb-4 mt-2 text-xl font-bold text-center">{{ $gettext('Latest additions') }}</h2>
      <div v-for="match in latest_entries" :key="match.entry_id">
        <EntryBox :record="match" />
      </div>
      <div class="mt-4 mx-auto text-center">
        <router-link :to="{ name: 'search', query: { query: '', page_number: 2 } }" class="btn-accent p-2 mx-2 rounded-sm">
          {{ $gettext('More') }}
        </router-link>
      </div>
    </div>
  </div>
</template>
