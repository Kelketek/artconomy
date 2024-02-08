<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p class="mb-0">
          <v-chip color="secondary" variant="flat" @click="search('refsheet')" class="mx-1">refsheet</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('badge')" class="mx-1">badge</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('stickers')" class="mx-1">stickers</v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import SearchHints from '@/components/views/search/mixins/SearchHints.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import Viewer from '@/mixins/viewer.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'

@Component({
  components: {
    AcExpandedProperty,
    AcBoundField,
  },
})
class ProductHints extends mixins(SearchHints, Viewer) {
}

export default toNative(ProductHints)
</script>
