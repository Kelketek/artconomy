<template>
  <ac-paginated :list="list" :track-pages="true" :auto-run="false">
    <v-flex sm6 md4 lg3 xl2 pa-2 v-for="character in list.list" :key="character.x.id">
      <ac-character-preview :character="character.x"></ac-character-preview>
    </v-flex>
    <v-flex text-xs-center slot="empty">
      <v-card>
        <v-card-text>
          We could not find anything which matched your request.
        </v-card-text>
      </v-card>
    </v-flex>
  </ac-paginated>
</template>
<script lang="ts">
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import {ListController} from '@/store/lists/controller'
import Component, {mixins} from 'vue-class-component'
import {Character} from '@/store/characters/types/Character'
import SearchList from '@/components/views/search/mixins/SearchList'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
  @Component({
    components: {AcCharacterPreview, AcPaginated},
  })
export default class SearchCharacters extends mixins(SearchList) {
    public list: ListController<Character> = null as unknown as ListController<Character>
    public created() {
      this.list = this.$getList('searchCharacters', {endpoint: '/api/profiles/v1/search/character/'})
    }
}
</script>
