<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <template v-slot:default>
      <v-col class="pa-2" sm="6" md="4" lg="3" xl="2" v-for="character in list.list" :key="character.x!.id">
        <ac-character-preview :character="character.x"></ac-character-preview>
      </v-col>
    </template>
    <template v-slot:empty>
      <v-col class="text-center">
        <v-card>
          <v-card-text>
            We could not find anything which matched your request.
          </v-card-text>
        </v-card>
      </v-col>
    </template>
  </ac-paginated>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller.ts'
import {Component, mixins, toNative} from 'vue-facing-decorator'
import {Character} from '@/store/characters/types/Character.ts'
import SearchList from '@/components/views/search/mixins/SearchList.ts'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'

@Component({
  components: {
    AcCharacterPreview,
    AcPaginated,
  },
})
class SearchCharacters extends mixins(SearchList) {
  public list: ListController<Character> = null as unknown as ListController<Character>

  public created() {
    this.list = this.$getList('searchCharacters', {
      endpoint: '/api/profiles/search/character/',
      persistent: true,
    })
  }
}

export default toNative(SearchCharacters)
</script>
