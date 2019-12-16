<template>
  <ac-paginated :list="watch" :track-pages="true">
    <v-col cols="3" sm="2" lg="1" v-for="user in watch.list" :key="user.x.id">
      <ac-avatar :user="user.x"></ac-avatar>
    </v-col>
  </ac-paginated>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import {Prop} from 'vue-property-decorator'
import {ListController} from '@/store/lists/controller'
import {User} from '@/store/profiles/types/User'
@Component({
  components: {AcAvatar, AcPaginated},
})
export default class WatchList extends mixins(Subjective) {
  public watch: ListController<User> = null as unknown as ListController<User>
  @Prop({required: true})
  public endpoint!: string
  @Prop({required: true})
  public nameSpace!: string

  public created() {
    this.watch = this.$getList(`${this.username}__${this.nameSpace}`, {endpoint: this.endpoint})
    this.watch.firstRun()
  }
}
</script>
