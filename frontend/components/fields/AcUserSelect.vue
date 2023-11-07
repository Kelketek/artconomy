<template>
  <v-autocomplete
      chips
      :multiple="multiple"
      v-model="tags"
      autocomplete
      v-model:search="query"
      :items="items"
      hide-no-data
      auto-select-first
      deletable-chips
      hide-selected
      cache-items
      :filter="itemFilter"
      :item-value="itemValue"
      :allow-raw="allowRaw"
      item-title="username"
      ref="input"
      v-bind="fieldAttrs"
  />
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import Autocomplete from '@/components/fields/mixins/autocomplete'

@Component({
  components: {AcAvatar},
})
class AcUserSelect extends mixins(Autocomplete) {
  public url = '/api/profiles/search/user/'
}

export default toNative(AcUserSelect)
</script>
