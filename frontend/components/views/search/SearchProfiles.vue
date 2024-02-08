<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-col cols="4" sm="3" md="2" lg="1" v-for="user in list.list" :key="user.x!.id">
      <ac-avatar :user="user.x"></ac-avatar>
    </v-col>
  </ac-paginated>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller.ts'
import {Component, mixins, toNative} from 'vue-facing-decorator'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import SearchList from '@/components/views/search/mixins/SearchList.ts'
import AcAvatar from '@/components/AcAvatar.vue'

@Component({
  components: {
    AcAvatar,
    AcPaginated,
  },
})
class SearchProfiles extends mixins(SearchList) {
  public list: ListController<TerseUser> = null as unknown as ListController<TerseUser>

  public created() {
    this.list = this.$getList('searchProfiles', {
      endpoint: '/api/profiles/search/user/',
      persistent: true,
    })
  }
}

export default toNative(SearchProfiles)
</script>
