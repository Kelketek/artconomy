<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-col cols="4" sm="3" md="2" lg="1" v-for="user in list.list" :key="user.x.id">
      <ac-avatar :user="user.x"></ac-avatar>
    </v-col>
  </ac-paginated>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import Component, {mixins} from 'vue-class-component'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import SearchList from '@/components/views/search/mixins/SearchList'
import AcAvatar from '@/components/AcAvatar.vue'
  @Component({
    components: {AcAvatar, AcPaginated},
  })
export default class SearchProfiles extends mixins(SearchList) {
    public list: ListController<TerseUser> = null as unknown as ListController<TerseUser>
    public created() {
      this.list = this.$getList('searchProfiles', {
        endpoint: '/api/profiles/v1/search/user/',
        persistent: true,
      })
    }
}
</script>
