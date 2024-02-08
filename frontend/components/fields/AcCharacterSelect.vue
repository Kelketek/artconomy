<template>
  <v-autocomplete
      :chips="true"
      :multiple="multiple"
      v-model="tags"
      autocomplete
      v-model:search="query"
      :items="items"
      :hide-no-data="true"
      :auto-select-first="true"
      closable-chips
      :hide-selected="true"
      cache-items
      :filter="itemFilter"
      item-value="id"
      :item-title="formatName"
      ref="input"
      v-bind="$attrs"
  />
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import {Character} from '@/store/characters/types/Character.ts'
import Viewer from '@/mixins/viewer.ts'
import Autocomplete from '@/components/fields/mixins/autocomplete.ts'

@Component({
  components: {AcAvatar},
})
class AcCharacterSelect extends mixins(Autocomplete, Viewer) {
  public url = '/api/profiles/search/character/'

  public formatName(_id: number, sourceItem: Character | '' | number) {
    const item = sourceItem || _id
    /* istanbul ignore if */
    if (Array.isArray(item) || !item) {
      // Type mismatch thrown by parent library. Return an empty string for this.
      return ''
    }
    if (typeof item === 'number') {
      return `${item}`
    }
    let text = item.name
    if (item.user.username !== this.rawViewerName) {
      text += ` (${item.user.username})`
    }
    return text
  }
}

export default toNative(AcCharacterSelect)
</script>
