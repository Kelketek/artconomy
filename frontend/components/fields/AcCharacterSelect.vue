<template>
    <v-autocomplete
        chips
        :multiple="multiple"
        v-model="tags"
        autocomplete
        v-bind:search-input.sync="query"
        :items="items"
        hide-no-data
        auto-select-first
        deletable-chips
        hide-selected
        cache-items
        :filter="itemFilter"
        item-value="id"
        :item-text="formatName"
        ref="input"
        v-bind="fieldAttrs"
    />
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcAvatar from '@/components/AcAvatar.vue'
import {Character} from '@/store/characters/types/Character'
import Viewer from '@/mixins/viewer'
import Autocomplete from '@/components/fields/mixins/autocomplete'
  @Component({
    components: {AcAvatar},
  })
export default class AcCharacterSelect extends mixins(Autocomplete, Viewer) {
    public url = '/api/profiles/search/character/'
    public formatName(item: Character) {
      /* istanbul ignore if */
      if (Array.isArray(item)) {
        // Type mismatch thrown by parent library. Return an empty string for this.
        return ''
      }
      let text = item.name
      if (item.user.username !== this.rawViewerName) {
        text += ` (${item.user.username})`
      }
      return text
    }
}
</script>
