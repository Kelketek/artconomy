<template>
  <v-col>
    <v-row no-gutters>
      <v-col class="text-center" cols="12">
        Try terms like:
        <p>
          <v-chip color="secondary" variant="flat" @click="search('fox')" class="mx-1">fox</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('wolf')" class="mx-1">wolf</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('male')" class="mx-1">male</v-chip>
          <v-chip color="secondary" variant="flat" @click="search('female')" class="mx-1">female</v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import SearchHints from '@/components/views/search/mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'

@Component({
  components: {
    AcExpandedProperty,
    AcBoundField,
  },
})
class CharacterExtra extends mixins(SearchHints, Viewer) {
}

export default toNative(CharacterExtra)
</script>
