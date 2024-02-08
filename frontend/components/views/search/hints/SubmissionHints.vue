<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p>
          <v-chip color="secondary" variant="flat" @click="search('fox')" class="mx-1">fox</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('pony')" class="mx-1">pony</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('chibi')" class="mx-1">chibi</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('refsheet')" class="mx-1">refsheet</v-chip>
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
class SubmissionHints extends mixins(SearchHints, Viewer) {
}

export default toNative(SubmissionHints)
</script>
