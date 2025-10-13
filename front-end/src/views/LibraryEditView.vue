<script>
 import NavBar from '../components/NavBar.vue'
 import NavFooter from '../components/NavFooter.vue'
 import LibraryEdit from '../components/LibraryEdit.vue'
 import DashboardTable from '../components/DashboardTable.vue'
 import UserCreation from '../components/UserCreation.vue'
 import CsvUpload from '../components/CsvUpload.vue'
 
 export default {
     components: {
         LibraryEdit,
         DashboardTable,
         UserCreation,
         CsvUpload,
         NavBar,
         NavFooter,
     },
     data() {
         return {
             user_list_key: this.$route.params.id,
         }
     },
     methods: {
         refresh_users() {
             console.log("Refreshing");
             this.user_list_key = this.user_list_key + '-x';
         },
     }
 }
</script>
<template>
  <NavBar />
  <main class="grow">
    <div class="m-8">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 ">
        <div class="mb-6">
          <LibraryEdit :library_id="$route.params.id" :key="$route.params.id" />
        </div>
        <div class="mb-6">
          <CsvUpload :library_id="$route.params.id" :key="$route.params.id" />
        </div>
        <div class="mb-6">
          <UserCreation :library_id="$route.params.id" :key="$route.params.id" @user-created="refresh_users"/>
        </div>
      </div>
      <DashboardTable :listing_url="'/collector/api/library/list-users/' + $route.params.id"
                      :removal_url="'/collector/api/library/remove-user/' + $route.params.id"
                      :table_title="$gettext('Library Users')"
                      :key="$route.params.id" />
    </div>
  </main>
  <NavFooter />
</template>
