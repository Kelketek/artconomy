<template>
  <v-container
    fluid
    class="pa-0"
  >
    <v-row dense>
      <v-col>
        <v-tooltip
          v-if="controls"
          top
          aria-label="Tooltip for tags"
        >
          <template #activator="activator">
            <v-btn
              color="primary"
              icon
              size="small"
              v-bind="activator.props"
              class="edit-button"
              aria-label="Edit tags"
              @click="editTags"
            >
              <v-icon
                size="x-large"
                :icon="mdiTagMultiple"
              />
            </v-btn>
          </template>
          Edit Tags
        </v-tooltip>
        <v-tooltip
          v-else
          top
          aria-label="Tooltip for tags"
        >
          <template #activator="activator">
            <v-icon
              v-bind="activator.props"
              :icon="mdiTagMultiple"
              aria-label="Tags"
            />
          </template>
          Tags
        </v-tooltip>
        <v-chip
          v-for="tag in displayedTags"
          :key="tag"
          class="tag-search-link ml-2"
          @click.stop="setSearch(tag)"
        >
          <ac-link :to="tagLink(tag)">
            {{ tag }}
          </ac-link>
        </v-chip>
        <v-chip
          v-if="moreTags"
          class="show-more-tags ml-2"
          @click="showMore"
        >
          ...
        </v-chip>
      </v-col>
      <v-col v-if="displayedTags.length === 0">
        <span>
          &nbsp;
          <span v-if="controls">No tags set. Please add some!</span>
          <span v-else>No tags set.</span>
        </span>
      </v-col>
      <ac-expanded-property
        v-model="toggle"
        aria-label="Tag Editing Dialog"
      >
        <template #title>
          All Tags
        </template>
        <v-row>
          <v-col
            v-if="editing && controls"
            cols="12"
          >
            <ac-patch-field
              field-type="ac-tag-field"
              :patcher="patcher"
              :autofocus="true"
            />
          </v-col>
          <v-col
            v-show="!editing"
            cols="12"
          >
            <v-chip
              v-for="tag in patcher.rawValue"
              :key="tag"
              variant="tonal"
              class="tag-search-link ml-2"
              @click.stop="setSearch(tag)"
            >
              <ac-link :to="tagLink(tag)">
                {{ tag }}
              </ac-link>
            </v-chip>
          </v-col>
        </v-row>
        <template #actions>
          <v-switch
            v-if="controls"
            v-model="editing"
            label="Editing"
            color="primary"
          />
          <v-spacer />
          <v-btn
            color="primary"
            type="submit"
            variant="flat"
          >
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
import {useForm} from '@/store/forms/hooks.ts'
import {useRouter} from 'vue-router'
import {useViewer} from '@/mixins/viewer.ts'
import {useSubject} from '@/mixins/subjective.ts'
import type {SubjectiveProps} from '@/types/main'

declare interface AcTagDisplayProps {
  patcher: Patch,
  editable?: boolean,
  scope: string,
}
const props = withDefaults(defineProps<AcTagDisplayProps & SubjectiveProps>(), {editable: false})

const {isRegistered, powers} = useViewer()
const {isCurrent} = useSubject({ props })

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
  return powers.value.moderate_content
})

const moreTags = computed(() => props.patcher.rawValue.length - displayedTags.value.length)
</script>
