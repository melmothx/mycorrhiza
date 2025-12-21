<script>
 import BugReport from './BugReport.vue'
 import ContactButton from './ContactButton.vue'
 import DocSite from './DocSite.vue'
 export default {
     components: {
         BugReport,
         ContactButton,
         DocSite,
     },
 }
</script>
<template>
  <footer class="mt-8 p-4 bg-linear-to-tr from-old-copper-200 to-old-copper-300">
    <div class="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(200px,1fr))]">
      <DocSite />
      <BugReport />
      <ContactButton />
    </div>
  </footer>
</template>
