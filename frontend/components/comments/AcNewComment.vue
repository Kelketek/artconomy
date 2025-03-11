<template>
  <v-card
    :class="{comment: true, 'elevation-3': alternate}"
    class="new-comment"
    :color="color"
  >
    <v-toolbar
      v-if="isRegistered || (isLoggedIn && guestOk)"
      dense
      color="black"
    >
      <ac-avatar
        :user="viewerUser"
        :show-name="false"
        class="ml-3"
      />
      <v-toolbar-title class="ml-1">
        <ac-link :to="profileLink(viewerUser)">
          {{ viewerName }}
        </ac-link>
      </v-toolbar-title>
      <v-spacer />
    </v-toolbar>
    <v-card-text>
      <v-row
        v-if="!isRegistered && !guestOk"
        no-gutters
      >
        <v-col
          class="text-center"
          cols="12"
        >
          <v-btn
            class="new-comment-button"
            :to="{name: 'Login', query: {next: route.fullPath}}"
            variant="elevated"
          >
            Log in or
            Register to
            Comment!
          </v-btn>
        </v-col>
      </v-row>
      <v-list-subheader v-else-if="!modelValue">
        New Comment
      </v-list-subheader>
      <v-row
        v-if="isRegistered || (isLoggedIn && guestOk)"
        no-gutters
      >
        <v-col
          cols="12"
          sm="12"
        >
          <ac-form-container v-bind="newCommentForm.bind">
            <ac-form @submit.prevent="publish">
              <ac-bound-field
                :field="newCommentForm.fields.text"
                field-type="ac-editor"
              >
                <template #actions>
                  <v-col class="text-right">
                    <v-row dense>
                      <v-spacer />
                      <v-col
                        v-if="modelValue"
                        class="shrink"
                      >
                        <v-tooltip top>
                          <template #activator="activator">
                            <v-btn
                              v-bind="activator.props"
                              color="danger"
                              icon
                              small
                              class="cancel-button"
                              @click="cancel"
                            >
                              <v-icon :icon="mdiCancel" />
                            </v-btn>
                          </template>
                          <span>Cancel</span>
                        </v-tooltip>
                      </v-col>
                      <v-col class="shrink">
                        <v-tooltip top>
                          <template #activator="activator">
                            <v-btn
                              v-bind="activator.props"
                              color="blue"
                              type="submit"
                              icon
                              class="submit-button"
                              small
                            >
                              <v-icon :icon="mdiSend" />
                            </v-btn>
                          </template>
                          <span>Send</span>
                        </v-tooltip>
                      </v-col>
                    </v-row>
                  </v-col>
                </template>
              </ac-bound-field>
            </ac-form>
          </ac-form-container>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import {useViewer} from '@/mixins/viewer.ts'
import {ListController} from '@/store/lists/controller.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {mdiCancel, mdiSend} from '@mdi/js'
import {computed, Ref, watch} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {profileLink} from '@/lib/otherFormatters.ts'
import {useTheme} from 'vuetify'
import {useRoute} from 'vue-router'
import type {Comment} from '@/types/main'
import {User} from '@/store/profiles/types/main'
import {RawData} from '@/store/forms/types/main'

const route = useRoute()

// Used for when we're nested under a comment thread.
const cancel = () => {
  emit('update:modelValue', false)
}

declare interface AcNewCommentProps {
  commentList: ListController<Comment>
  alternate?: boolean,
  modelValue?: boolean,
  guestOk?: boolean,
  extraData?: RawData,
}

const props = withDefaults(
    defineProps<AcNewCommentProps>(),
    {
      alternate: false,
      modelValue: false,
      guestOk: false,
      extraData: () => ({}),
    }
)

const theme = useTheme()

const color = computed(() => {
  if (props.alternate) {
    return theme.current.value.colors['well-darken-4']
  }
  return ''
})

const emit = defineEmits<{'update:modelValue': [false]}>()
const {viewer, isLoggedIn, isRegistered, viewerName} = useViewer()

const viewerUser =  viewer as Ref<User>

const newCommentForm = useForm(props.commentList.name.value + '_new', {
  endpoint: props.commentList.endpoint,
  fields: {
    text: {value: ''},
    extra_data: {value: props.extraData},
  },
})

const publish = () => {
  newCommentForm.submit().then(props.commentList.push).then(cancel).catch(newCommentForm.setErrors)
}

watch(() => props.extraData, () => {
  newCommentForm.fields.extra_data.update(props.extraData)
}, {deep: true})
</script>

<style lang="stylus" scoped>
.theme--dark .comment.alternate {
  background-color: var(--v-well-darken-2)
}
</style>
