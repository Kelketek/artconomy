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
      :item-value="itemValue"
      :allow-raw="allowRaw"
      item-text="username"
      ref="input"
      v-bind="fieldAttrs"
  />
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcAvatar from '@/components/AcAvatar.vue'
import Autocomplete from '@/components/fields/mixins/autocomplete'
import {Prop} from 'vue-property-decorator'
  @Component({
    components: {AcAvatar},
  })
export default class AcUserSelect extends mixins(Autocomplete) {
  public url = '/api/profiles/search/user/'
}
</script>
