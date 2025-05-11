<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import L from "leaflet";
 import "leaflet/dist/leaflet.css";
 import "leaflet.markercluster/dist/leaflet.markercluster.js";
 import "leaflet.markercluster/dist/MarkerCluster.css";
 import "leaflet.markercluster/dist/MarkerCluster.Default.css";
 export default {
     data() {
         return {
             map: null,
             marker_cluster_group: null,
             msg: null,
             areas: [
                 {
                     title: "Europa",
                     coords: "400,271,320,395,370,410,425,415,495,400,510,375,500,325,460,290",
                     center: [46.0037, 8.9511],
                 },
                 {
                     title: "Asia",
                     coords: "411,0,411,197,400,271,460,290,500,325,510,375,495,400,520,440,575,440,650,475,675,415,790,475,925,425,980,470,930,515,915,700,1030,865,1200,880,1200,0",
                     center: [39.9042, 116.4074],
                 },
                 {
                     title: "Africa",
                     coords: "370,410,425,415,495,400,520,440,575,440,575,580,470,650,345,490",
                     center: [-4.4419, 15.2663],
                 },
                 {
                     title: "Oceania",
                     coords: "650,475,675,415,790,475,925,425,980,470,930,515,915,700,735,785,660,625",
                     center: [-33.8688, 151.2093],
                 },
                 {
                     title: "North America East",
                     coords: "0,0,411,0,411,197,400,271,320,395,155,395,70,380,0,371",
                     center: [ 40.7128, -74.0060 ],
                 },
                 {
                     title: "Center America East",
                     coords: "320,395,155,395,70,380,0,371,0,585,152,480,228,480",
                     center: [ 20.6597, -103.3496 ],
                 },
                 {
                     title: "North America West",
                     coords: "960,1200,815,1000,1030,865,1200,880,1200,1200",
                     center: [ 34.0522, -118.2437 ],
                 },
                 {
                     title: "Center America West",
                     coords: "665,1040,725,1200,960,1200,815,1000",
                     center: [ 21.5218, -77.7812 ],
                 },
                 {
                     title: "South America",
                     coords: "0,585,152,480,228,480,375,575,520,770,665,1040,725,1200,0,1200",
                     center: [ -34.0637, -58.3816 ],
                 },
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
         handle_area_click(event) {
             event.preventDefault();
             const idx = event.currentTarget.dataset.idx;
             const target = this.areas[idx];
             console.log(target.title);
             this.map.setView(target.center, 4);
         },
     },
     beforeUnmount() {
         console.log("Unmounting");
         this.$refs.areas.forEach(el => {
            el.removeEventListener('click', this.handle_area_click);
         });
     },
     mounted() {
         this.$refs.areas.forEach(el => {
             el.addEventListener('click', this.handle_area_click);
         });
         this.map = L.map(this.$refs.mapContainer, { minZoom: 4 });
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
  <img src="/spilhaus.jpg" usemap="#spilhaus-map">
  <map id="spilhaus-map">
    <area v-for="(area, index) in areas"
          :key="index"
          :data-idx="index"
          :title="area.title"
          :coords="area.coords"
          shape="poly"
          href="#"
          :alt="area.title"
          ref="areas"
    />
  </map>
  <div ref="mapContainer" style="height: 600px"></div>
</template>
