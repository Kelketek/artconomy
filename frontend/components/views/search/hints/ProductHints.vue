<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12" >
        Try terms like:
        <p class="mb-0"><v-chip color="secondary" @click="search('winter_holiday')" class="mx-1">winter_holiday</v-chip>
        <v-chip color="secondary" @click="search('ych')" class="mx-1">ych</v-chip>
        <v-chip color="secondary" @click="search('stickers')" class="mx-1">stickers</v-chip></p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import SearchHints from '@/components/views/search/mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
  @Component({
    components: {AcExpandedProperty, AcBoundField},
  })
export default class ProductHints extends mixins(SearchHints, Viewer) {
}
</script>
