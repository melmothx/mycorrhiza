<script>
 import axios from 'axios'
 axios.defaults.xsrfCookieName = "csrftoken";
 axios.defaults.xsrfHeaderName = "X-CSRFToken";
 import L from "leaflet";
 import "leaflet/dist/leaflet.css";
 export default {
     data() {
         return {
             map: null,
             marker_layer_group: null,
         }
     },
     methods: {
         async fetch_markers() {
             const res = await axios.get('/collector/api/libraries');
             const markers = res.data.libraries.filter((l) => l.latitude && l.longitude)
             console.log(markers);
             markers.forEach(m => {
                 const div = document.createElement("div")
                 const link = document.createElement("a");
                 link.textContent = m.name
                 link.href = `/library/details/${m.id}`;
                 link.target = "_blank";
                 div.appendChild(link);
                 L.marker([m.latitude, m.longitude])
                  .addTo(this.marker_layer_group)
                 .bindPopup(div)
             })
         }
     },
     mounted() {
         this.map = L.map(this.$refs.mapContainer).setView([51.505, -0.09], 13);
         L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
             attribution:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
         }).addTo(this.map)
         this.marker_layer_group = L.layerGroup().addTo(this.map);
         this.fetch_markers();
     }
 }
</script>
<style>
 .leaflet-control-attribution .leaflet-attribution-flag {
     display: none !important;
 }
</style>
<template>
  <div ref="mapContainer" style="height: 400px"></div>

</template>
