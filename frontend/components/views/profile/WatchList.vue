<template>
  <ac-paginated :list="watch" :track-pages="true">
    <v-row>
      <v-col cols="3" sm="2" lg="1" v-for="user in watch.list" :key="user.x!.id">
        <ac-avatar :user="user.x" />
      </v-col>
    </v-row>
  </ac-paginated>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import {ListController} from '@/store/lists/controller'
import {User} from '@/store/profiles/types/User'
import {flatten} from '@/lib/lib'

@Component({
  components: {
    AcAvatar,
    AcPaginated,
  },
})
class WatchList extends mixins(Subjective) {
  public watch: ListController<User> = null as unknown as ListController<User>
  @Prop({required: true})
  public endpoint!: string

  @Prop({required: true})
  public nameSpace!: string

  public created() {
    this.watch = this.$getList(`${flatten(this.username)}__${this.nameSpace}`, {endpoint: this.endpoint})
    this.watch.firstRun()
  }
}

export default toNative(WatchList)
</script>
