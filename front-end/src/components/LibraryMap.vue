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
 delete L.Icon.Default.prototype._getIconUrl;
 L.Icon.Default.mergeOptions({
     iconRetinaUrl: markerIcon2x,
     iconUrl: markerIcon,
     shadowUrl: markerShadow,
 });
 export default {
     data() {
         return {
             map: null,
             marker_cluster_group: null,
             msg: null,
             imgWidth: 1200,
             imgHeight: 1200,
             areas: [
                 {
                     alt: "Europa",
                     title: "Europa",
                     coords: "400,271 320,395 370,410 425,415 495,400 510,375 500,325 460,290",
                     center: [46.0037, 8.9511],
                     fill: "deepskyblue", stroke: "blue"
                 },
                 {
                     alt: "Asia",
                     title: "Asia",
                     coords: "411,0 411,197 400,271 460,290 500,325 510,375 495,400 520,440 575,440 650,475 675,415 790,475 925,425 980,470 930,515 915,700 1030,865 1200,880 1200,0",
                     center: [39.9042, 116.4074],
                     fill: "yellow", stroke: "goldenrod"
                 },
                 {
                     alt: "Africa",
                     title: "Africa",
                     center: [-4.4419, 15.2663],
                     coords: "370,410 425,415 495,400 520,440 575,440 575,580 470,650 345,490",
                     fill: "orange", stroke: "orangered"
                 },
                 {
                     alt: "Oceania",
                     title: "Oceania",
                     coords: "650,475 675,415 790,475 925,425 980,470 930,515 915,700 735,785 660,625",
                     center: [-33.8688, 151.2093],
                     fill: "green", stroke: "darkgreen"
                 },
                 {
                     alt: "North America East",
                     title: "North America East",
                     coords: "0,0 411,0 411,197 400,271 320,395 155,395 70,380 0,371",
                     center: [ 40.7128, -74.0060 ],
                     fill: "purple", stroke: "indigo"
                 },
                 {
                     alt: "Center America East",
                     title: "Center America East",
                     coords: "320,395 155,395 70,380 0,371 0,585 152,480 228,480",
                     center: [ 20.6597, -103.3496 ],
                     fill: "pink", stroke: "mediumvioletred"
                 },
                 {
                     alt: "North America West",
                     title: "North America West",
                     coords: "960,1200 815,1000 1030,865 1200,880 1200,1200",
                     center: [ 34.0522, -118.2437 ],
                     fill: "lightblue", stroke: "blue"
                 },
                 {
                     alt: "Center America West",
                     title: "Center America West",
                     coords: "665,1040 725,1200 960,1200 815,1000",
                     center: [ 21.5218, -77.7812 ],
                     fill: "brown", stroke: "chocolate"
                 },
                 {
                     alt: "South America",
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
                 link.textContent = m.name
                 link.href = `/library/details/${m.id}`;
                 link.target = "_blank";
                 div.appendChild(link);
                 L.marker([m.latitude, m.longitude])
                  .addTo(this.marker_cluster_group)
                 .bindPopup(div)
             })
         },
         handle_area_click(area) {
             this.map.setView(area.center, 4);
         },
     },
     mounted() {
         this.map = L.map(this.$refs.mapContainer, { minZoom: 1 });
         this.map.setView(this.areas[0].center, 4);
         L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
             attribution:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
         }).addTo(this.map);
         this.marker_cluster_group = L.markerClusterGroup();
         this.marker_cluster_group.addTo(this.map);
         this.fetch_markers();
     },
 }
</script>
<style>
 .leaflet-control-attribution .leaflet-attribution-flag {
     display: none !important;
 }
</style>
<template>
  <div class="m-2 grid sm:grid-cols-[200px_auto] gap-2">
    <div class="hidden sm:block">
      <svg
          class="border-4 border-cab-sav-800 rounded-sm"
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
          <title>{{ area.title }}</title>
        </polygon>
      </svg>
    </div>
    <div ref="mapContainer" style="height: 600px"></div>
  </div>
</template>
