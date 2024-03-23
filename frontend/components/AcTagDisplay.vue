<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-container fluid class="pa-0">
    <v-row dense>
      <v-col>
        <v-tooltip top v-if="controls" aria-label="Tooltip for tags">
          <template v-slot:activator="{props}">
            <v-btn color="primary" icon size="small" v-bind="props" @click="editTags" class="edit-button" aria-label="Edit tags">
              <v-icon size="x-large" :icon="mdiTagMultiple"/>
            </v-btn>
          </template>
          Edit Tags
        </v-tooltip>
        <v-tooltip top v-else aria-label="Tooltip for tags">
          <template v-slot:activator="{props}">
            <v-icon v-bind="props" :icon="mdiTagMultiple" aria-label="Tags"/>
          </template>
          Tags
        </v-tooltip>
        <v-chip v-for="tag in displayedTags" :key="tag" @click.stop="setSearch(tag)" class="tag-search-link ml-2">
          <ac-link :to="tagLink(tag)">{{tag}}</ac-link>
        </v-chip>
        <v-chip v-if="moreTags" @click="showMore" class="show-more-tags ml-2">...</v-chip>
      </v-col>
      <v-col v-if="displayedTags.length === 0">
        <span>
          &nbsp;
          <span v-if="controls">No tags set. Please add some!</span>
          <span v-else>No tags set.</span>
        </span>
      </v-col>
      <ac-expanded-property v-model="toggle" aria-label="Tag Editing Dialog">
        <template v-slot:title>
          All Tags
        </template>
        <v-row>
          <v-col cols="12" v-if="editing && controls">
            <ac-patch-field field-type="ac-tag-field" :patcher="patcher"/>
          </v-col>
          <v-col cols="12" v-show="!editing">
            <v-chip v-for="tag in patcher.rawValue" :key="tag" class="mx-1" :color="$vuetify.theme.current.colors['well-darken-4']">
              <ac-link :to="tagLink(tag)">{{tag}}</ac-link>
            </v-chip>
          </v-col>
        </v-row>
        <template v-slot:actions>
          <v-switch v-model="editing" label="Editing" v-if="controls" color="primary"/>
          <v-spacer/>
          <v-btn color="primary" type="submit" variant="flat">
            Done
          </v-btn>
        </template>
      </ac-expanded-property>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import {Patch} from '@/store/singles/patcher.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {mdiTagMultiple} from '@mdi/js'
import {computed, ref} from 'vue'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useRouter} from 'vue-router'
import {useViewer} from '@/mixins/viewer.ts'
import {useSubject} from '@/mixins/subjective.ts'

declare interface AcTagDisplayProps {
  patcher: Patch,
  editable?: boolean,
  scope: string,
}

const props = withDefaults(defineProps<AcTagDisplayProps & SubjectiveProps>(), {editable: false})

const {isRegistered, isStaff} = useViewer()
const {isCurrent} = useSubject(props)

const router = useRouter()

const toggle = ref(false)
const editing = ref(false)

const editTags = () => {
  toggle.value = true
  editing.value = true
}

const showMore = () => {
  editing.value = false
  toggle.value = true
}

const tagLink = (tag: string) => {
  return {
    name: 'Search' + props.scope,
    query: {q: tag},
  }
}

const setSearch = (tag: string) => {
  searchForm.reset()
  searchForm.fields.q.update(tag)
  router.push(tagLink(tag))
}

const searchForm = useForm('search')

const displayedTags = computed(() => props.patcher.rawValue.slice(0, 10))

const controls = computed(() => {
  if (props.editable && isRegistered.value) {
    return true
  }
  if (isCurrent.value) {
    return true
  }
  return isStaff.value
})

const moreTags = computed(() => props.patcher.rawValue.length - displayedTags.value.length)
</script>
